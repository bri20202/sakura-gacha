from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    pulls = relationship("Pull", back_populates="user")
    inventory = relationship("Inventory", back_populates="user")


class Banner(Base):
    __tablename__ = "banners"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    items = relationship("Item", back_populates="banner")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    rarity = Column(String, nullable=False)  # Common, Rare, Epic, Legendary
    drop_rate = Column(Float, nullable=False)
    emoji = Column(String, default="🌸")
    banner_id = Column(Integer, ForeignKey("banners.id"), nullable=False)

    banner = relationship("Banner", back_populates="items")


class Pull(Base):
    __tablename__ = "pulls"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    banner_id = Column(Integer, ForeignKey("banners.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    pull_number = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="pulls")
    banner = relationship("Banner")
    item = relationship("Item")


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    quantity = Column(Integer, default=1)

    user = relationship("User", back_populates="inventory")
    item = relationship("Item")
