from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship

from app.db.base import Base


class ContractMaster(Base):
    __tablename__ = "ContractMaster"

    contract_no: Mapped[str] = mapped_column(String(30), primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contract_status: Mapped[str] = mapped_column(String(30), nullable=False, default="ACTIVE")

    total_outstanding_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, default=Decimal("0.00")
    )

    line_user_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True, unique=True, index=True
    )
    line_display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    line_map_status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="UNMAPPED"
    )
    line_notify_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    line_mapped_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
    payments: Mapped[list["PaymentSchedule"]] = relationship(
    "PaymentSchedule",
    back_populates="contract",
)