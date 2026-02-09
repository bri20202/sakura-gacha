from datetime import datetime
from pydantic import BaseModel


# ── Auth ─────────────────────────────────────────────────
class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Banner / Item ────────────────────────────────────────
class ItemResponse(BaseModel):
    id: int
    name: str
    rarity: str
    drop_rate: float
    emoji: str

    model_config = {"from_attributes": True}


class BannerResponse(BaseModel):
    id: int
    name: str
    description: str
    is_active: bool

    model_config = {"from_attributes": True}


class BannerDetailResponse(BannerResponse):
    items: list[ItemResponse]


# ── Pull ─────────────────────────────────────────────────
class PullResultResponse(BaseModel):
    item_name: str
    rarity: str
    emoji: str
    is_pity: bool


class MultiPullResponse(BaseModel):
    results: list[PullResultResponse]
    total_pulls: int


# ── Inventory ────────────────────────────────────────────
class InventoryItemResponse(BaseModel):
    item_name: str
    rarity: str
    emoji: str
    quantity: int


# ── History ──────────────────────────────────────────────
class PullHistoryResponse(BaseModel):
    item_name: str
    rarity: str
    emoji: str
    banner_name: str
    pulled_at: datetime


# ── Stats ────────────────────────────────────────────────
class StatsResponse(BaseModel):
    total_pulls: int
    common_count: int
    rare_count: int
    epic_count: int
    legendary_count: int
    luck_rating: str
    pity_counter_epic: int
    pity_counter_legendary: int
