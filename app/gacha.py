import random
from sqlalchemy.orm import Session
from app.models import Item, Pull, Inventory

EPIC_PITY_THRESHOLD = 50
LEGENDARY_PITY_THRESHOLD = 90


def _get_pity_counters(db: Session, user_id: int, banner_id: int) -> tuple[int, int]:
    """Count pulls since last Epic and last Legendary for this user+banner."""
    pulls = (
        db.query(Pull)
        .filter(Pull.user_id == user_id, Pull.banner_id == banner_id)
        .order_by(Pull.pull_number.desc())
        .all()
    )

    since_epic = 0
    since_legendary = 0
    found_epic = False
    found_legendary = False

    for p in pulls:
        item = db.query(Item).filter(Item.id == p.item_id).first()
        if not found_epic:
            if item.rarity == "Epic" or item.rarity == "Legendary":
                found_epic = True
            else:
                since_epic += 1
        if not found_legendary:
            if item.rarity == "Legendary":
                found_legendary = True
            else:
                since_legendary += 1
        if found_epic and found_legendary:
            break

    return since_epic, since_legendary


def _pick_item(items: list[Item], force_rarity: str | None = None) -> Item:
    """Weighted random pick from item pool, optionally forcing a rarity tier."""
    if force_rarity:
        pool = [i for i in items if i.rarity == force_rarity]
        if pool:
            return random.choice(pool)

    weights = [i.drop_rate for i in items]
    return random.choices(items, weights=weights, k=1)[0]


def do_pull(
    db: Session, user_id: int, banner_id: int, items: list[Item]
) -> tuple[Item, bool]:
    """
    Execute a single gacha pull with pity system.
    Returns (item, was_pity).
    """
    since_epic, since_legendary = _get_pity_counters(db, user_id, banner_id)

    is_pity = False
    forced_rarity = None

    if since_legendary >= LEGENDARY_PITY_THRESHOLD - 1:
        forced_rarity = "Legendary"
        is_pity = True
    elif since_epic >= EPIC_PITY_THRESHOLD - 1:
        forced_rarity = "Epic"
        is_pity = True

    item = _pick_item(items, force_rarity=forced_rarity)

    # Determine pull number
    last_pull = (
        db.query(Pull)
        .filter(Pull.user_id == user_id)
        .order_by(Pull.pull_number.desc())
        .first()
    )
    pull_number = (last_pull.pull_number + 1) if last_pull else 1

    # Record pull
    pull = Pull(
        user_id=user_id,
        banner_id=banner_id,
        item_id=item.id,
        pull_number=pull_number,
    )
    db.add(pull)

    # Update inventory
    inv = (
        db.query(Inventory)
        .filter(Inventory.user_id == user_id, Inventory.item_id == item.id)
        .first()
    )
    if inv:
        inv.quantity += 1
    else:
        db.add(Inventory(user_id=user_id, item_id=item.id, quantity=1))

    db.flush()
    return item, is_pity


def do_multi_pull(
    db: Session, user_id: int, banner_id: int, items: list[Item], count: int = 10
) -> list[tuple[Item, bool]]:
    """
    Execute multiple pulls. Guarantees at least one Rare+ in a 10-pull.
    """
    results = []
    for _ in range(count):
        item, is_pity = do_pull(db, user_id, banner_id, items)
        results.append((item, is_pity))

    # 10-pull guarantee: if no Rare or above, replace last Common with a Rare
    if count == 10:
        rarities = [r[0].rarity for r in results]
        has_rare_plus = any(r in ("Rare", "Epic", "Legendary") for r in rarities)
        if not has_rare_plus:
            rare_item = _pick_item(items, force_rarity="Rare")
            last_item, _ = results[-1]

            # Fix inventory: undo the common, add the rare
            inv_old = (
                db.query(Inventory)
                .filter(Inventory.user_id == user_id, Inventory.item_id == last_item.id)
                .first()
            )
            if inv_old:
                inv_old.quantity = max(0, inv_old.quantity - 1)

            inv_new = (
                db.query(Inventory)
                .filter(Inventory.user_id == user_id, Inventory.item_id == rare_item.id)
                .first()
            )
            if inv_new:
                inv_new.quantity += 1
            else:
                db.add(Inventory(user_id=user_id, item_id=rare_item.id, quantity=1))

            # Fix pull record
            last_pull = (
                db.query(Pull)
                .filter(Pull.user_id == user_id)
                .order_by(Pull.pull_number.desc())
                .first()
            )
            if last_pull:
                last_pull.item_id = rare_item.id

            results[-1] = (rare_item, True)
            db.flush()

    return results
