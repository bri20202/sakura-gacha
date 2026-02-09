from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import engine, get_db, Base
from app.models import User, Banner, Item, Pull, Inventory
from app.schemas import (
    UserCreate, UserResponse, Token,
    BannerResponse, BannerDetailResponse,
    PullResultResponse, MultiPullResponse,
    InventoryItemResponse, PullHistoryResponse, StatsResponse,
)
from app.auth import hash_password, verify_password, create_access_token, get_current_user
from app.gacha import do_pull, do_multi_pull

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sakura Gacha API",
    description="A gacha/loot-box pull simulator with pity system, inventory tracking, and pull statistics.",
    version="1.0.0",
)


# ── Root ─────────────────────────────────────────────────
@app.get("/", tags=["Root"])
def root():
    return {
        "name": "Sakura Gacha API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "register": "POST /auth/register",
            "login": "POST /auth/login",
            "banners": "GET /banners",
            "pull": "POST /banners/{id}/pull",
            "pull_ten": "POST /banners/{id}/pull/ten",
            "inventory": "GET /inventory",
            "history": "GET /history",
            "stats": "GET /stats",
        },
    }


# ── Auth ─────────────────────────────────────────────────
@app.post("/auth/register", response_model=UserResponse, status_code=201, tags=["Auth"])
def register(body: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    user = User(username=body.username, hashed_password=hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=Token, tags=["Auth"])
def login(body: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return Token(access_token=create_access_token(user.id))


# ── Banners ──────────────────────────────────────────────
@app.get("/banners", response_model=list[BannerResponse], tags=["Banners"])
def list_banners(db: Session = Depends(get_db)):
    return db.query(Banner).filter(Banner.is_active == True).all()


@app.get("/banners/{banner_id}", response_model=BannerDetailResponse, tags=["Banners"])
def get_banner(banner_id: int, db: Session = Depends(get_db)):
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    return banner


# ── Pulling ──────────────────────────────────────────────
@app.post("/banners/{banner_id}/pull", response_model=PullResultResponse, tags=["Gacha"])
def pull_one(banner_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    banner = db.query(Banner).filter(Banner.id == banner_id, Banner.is_active == True).first()
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found or inactive")
    items = db.query(Item).filter(Item.banner_id == banner_id).all()
    if not items:
        raise HTTPException(status_code=404, detail="No items in this banner")

    item, is_pity = do_pull(db, user.id, banner_id, items)
    db.commit()
    return PullResultResponse(item_name=item.name, rarity=item.rarity, emoji=item.emoji, is_pity=is_pity)


@app.post("/banners/{banner_id}/pull/ten", response_model=MultiPullResponse, tags=["Gacha"])
def pull_ten(banner_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    banner = db.query(Banner).filter(Banner.id == banner_id, Banner.is_active == True).first()
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found or inactive")
    items = db.query(Item).filter(Item.banner_id == banner_id).all()
    if not items:
        raise HTTPException(status_code=404, detail="No items in this banner")

    results = do_multi_pull(db, user.id, banner_id, items)
    db.commit()

    total = db.query(Pull).filter(Pull.user_id == user.id).count()
    return MultiPullResponse(
        results=[
            PullResultResponse(item_name=i.name, rarity=i.rarity, emoji=i.emoji, is_pity=p)
            for i, p in results
        ],
        total_pulls=total,
    )


# ── Inventory ────────────────────────────────────────────
@app.get("/inventory", response_model=list[InventoryItemResponse], tags=["Collection"])
def get_inventory(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    inv = db.query(Inventory).filter(Inventory.user_id == user.id).all()
    return [
        InventoryItemResponse(
            item_name=entry.item.name,
            rarity=entry.item.rarity,
            emoji=entry.item.emoji,
            quantity=entry.quantity,
        )
        for entry in inv
    ]


# ── Pull History ─────────────────────────────────────────
@app.get("/history", response_model=list[PullHistoryResponse], tags=["Collection"])
def get_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    pulls = (
        db.query(Pull)
        .filter(Pull.user_id == user.id)
        .order_by(Pull.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        PullHistoryResponse(
            item_name=p.item.name,
            rarity=p.item.rarity,
            emoji=p.item.emoji,
            banner_name=p.banner.name,
            pulled_at=p.created_at,
        )
        for p in pulls
    ]


# ── Stats ────────────────────────────────────────────────
@app.get("/stats", response_model=StatsResponse, tags=["Collection"])
def get_stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    pulls = db.query(Pull).filter(Pull.user_id == user.id).all()
    total = len(pulls)

    counts = {"Common": 0, "Rare": 0, "Epic": 0, "Legendary": 0}
    for p in pulls:
        counts[p.item.rarity] = counts.get(p.item.rarity, 0) + 1

    # Calculate luck rating
    if total == 0:
        luck = "No pulls yet"
    else:
        legendary_rate = counts["Legendary"] / total
        epic_rate = counts["Epic"] / total
        if legendary_rate > 0.04:
            luck = "Blessed by the Sakura Spirit"
        elif epic_rate > 0.12:
            luck = "Fortunate"
        elif legendary_rate > 0.02 or epic_rate > 0.08:
            luck = "Average"
        else:
            luck = "The blossoms will bloom soon..."

    # Pity counters
    since_epic = 0
    since_legendary = 0
    sorted_pulls = sorted(pulls, key=lambda p: p.pull_number, reverse=True)
    for p in sorted_pulls:
        if p.item.rarity in ("Epic", "Legendary"):
            break
        since_epic += 1
    for p in sorted_pulls:
        if p.item.rarity == "Legendary":
            break
        since_legendary += 1

    return StatsResponse(
        total_pulls=total,
        common_count=counts["Common"],
        rare_count=counts["Rare"],
        epic_count=counts["Epic"],
        legendary_count=counts["Legendary"],
        luck_rating=luck,
        pity_counter_epic=since_epic,
        pity_counter_legendary=since_legendary,
    )
