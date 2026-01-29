from __future__ import annotations
import enum
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nomUtil: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    idUtil: Mapped[str | None] = mapped_column(String(50), unique=True, index=True, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")


    @property
    def roles(self):
        return [user_role.role.name for user_role in self.user_roles]

    def has_role(self, role_name: str) -> bool:
        return any(user_role.role.name.value == role_name for user_role in self.user_roles)