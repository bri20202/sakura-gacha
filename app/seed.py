"""Seed the database with banners and items. Run with: python -m app.seed"""
from app.database import engine, SessionLocal, Base
from app.models import Banner, Item


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Clear existing seed data
    db.query(Item).delete()
    db.query(Banner).delete()

    # ── Spring Blossom Banner ────────────────────────────
    spring = Banner(
        name="Spring Blossom",
        description="Petals drift on a warm breeze. What treasures hide among the branches?",
        is_active=True,
    )
    db.add(spring)
    db.flush()

    spring_items = [
        # Common — 70% total
        Item(name="Fallen Petal",     rarity="Common",    drop_rate=20.0, emoji="🌸", banner_id=spring.id),
        Item(name="Cherry Leaf",      rarity="Common",    drop_rate=20.0, emoji="🍃", banner_id=spring.id),
        Item(name="Pink Dewdrop",     rarity="Common",    drop_rate=15.0, emoji="💧", banner_id=spring.id),
        Item(name="Blossom Seed",     rarity="Common",    drop_rate=15.0, emoji="🌱", banner_id=spring.id),
        # Rare — 20% total
        Item(name="Moonlit Branch",   rarity="Rare",      drop_rate=8.0,  emoji="🌙", banner_id=spring.id),
        Item(name="Sakura Lantern",   rarity="Rare",      drop_rate=7.0,  emoji="🏮", banner_id=spring.id),
        Item(name="Koi Pond Stone",   rarity="Rare",      drop_rate=5.0,  emoji="🪨", banner_id=spring.id),
        # Epic — 8% total
        Item(name="Enchanted Parasol", rarity="Epic",     drop_rate=5.0,  emoji="🌂", banner_id=spring.id),
        Item(name="Spirit Fox Mask",   rarity="Epic",     drop_rate=3.0,  emoji="🦊", banner_id=spring.id),
        # Legendary — 2% total
        Item(name="Eternal Sakura Tree",    rarity="Legendary", drop_rate=1.2, emoji="🌳", banner_id=spring.id),
        Item(name="Dragon of the Blossoms", rarity="Legendary", drop_rate=0.8, emoji="🐉", banner_id=spring.id),
    ]
    db.add_all(spring_items)

    # ── Midnight Garden Banner ───────────────────────────
    midnight = Banner(
        name="Midnight Garden",
        description="Under a moonless sky, the garden reveals its secrets to the brave.",
        is_active=True,
    )
    db.add(midnight)
    db.flush()

    midnight_items = [
        # Common — 70%
        Item(name="Shadow Petal",     rarity="Common",    drop_rate=18.0, emoji="🖤", banner_id=midnight.id),
        Item(name="Night Moss",       rarity="Common",    drop_rate=18.0, emoji="🌿", banner_id=midnight.id),
        Item(name="Firefly Jar",      rarity="Common",    drop_rate=17.0, emoji="✨", banner_id=midnight.id),
        Item(name="Dusk Stone",       rarity="Common",    drop_rate=17.0, emoji="🪨", banner_id=midnight.id),
        # Rare — 20%
        Item(name="Phantom Koi",      rarity="Rare",      drop_rate=8.0,  emoji="🐟", banner_id=midnight.id),
        Item(name="Wisteria Crown",   rarity="Rare",      drop_rate=7.0,  emoji="👑", banner_id=midnight.id),
        Item(name="Moonstone Ring",   rarity="Rare",      drop_rate=5.0,  emoji="💍", banner_id=midnight.id),
        # Epic — 8%
        Item(name="Void Lantern",     rarity="Epic",      drop_rate=5.0,  emoji="🔮", banner_id=midnight.id),
        Item(name="Oni War Fan",      rarity="Epic",      drop_rate=3.0,  emoji="🎌", banner_id=midnight.id),
        # Legendary — 2%
        Item(name="Celestial Moon Blade", rarity="Legendary", drop_rate=1.2, emoji="🌕", banner_id=midnight.id),
        Item(name="The Nine-Tailed Spirit", rarity="Legendary", drop_rate=0.8, emoji="🦊", banner_id=midnight.id),
    ]
    db.add_all(midnight_items)

    db.commit()
    db.close()
    print("Database seeded with 2 banners and 22 items!")


if __name__ == "__main__":
    seed()
