from __future__ import annotations
from app.db.base import Base
import sqlalchemy.orm import Mapped, mapped_column, relationship
import sqlalchemy import Integer, ForeignKey, UniqueConstraint

class UserRole(Base):
    __tablename__ = "user_role"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete='CASCADE'))
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), ondelete='CASCADE')

    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_role"),)

    user = relationship("User", back_populates="user_roles")
    role = relationship("Role")
