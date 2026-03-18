from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PaymentSchedule(Base):
    __tablename__ = "payment_schedules"
    __table_args__ = (
        UniqueConstraint("contract_no", "billing_date", name="uq_contract_billing_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    contract_no: Mapped[str] = mapped_column(ForeignKey("ContractMaster.contract_no"), nullable=False, index=True)

    billing_seq: Mapped[int] = mapped_column(Integer, nullable=False)
    billing_date: Mapped[date] = mapped_column(Date, nullable=False)

    daily_rent_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    outstanding_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)

    payment_status: Mapped[str] = mapped_column(String(20), nullable=False, default="UNPAID")
    payment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    receipt_no: Mapped[str | None] = mapped_column(String(50), nullable=True)

    sent_line_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sent_line_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    contract: Mapped["ContractMaster"] = relationship(back_populates="payments")


class ApiLog(Base):
    __tablename__ = "api_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    api_name: Mapped[str] = mapped_column(String(100), nullable=False)
    request_ref: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    contract_no: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)
    line_user_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)

    api_direction: Mapped[str | None] = mapped_column(String(20), nullable=True)
    source_system: Mapped[str | None] = mapped_column(String(50), nullable=True)
    target_system: Mapped[str | None] = mapped_column(String(50), nullable=True)

    request_payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_code: Mapped[str] = mapped_column(String(30), nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)