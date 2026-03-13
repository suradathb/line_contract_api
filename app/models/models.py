from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Contract(Base):
    __tablename__ = "contracts"

    contract_no: Mapped[str] = mapped_column(String(30), primary_key=True)
    customer_id: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    id_card_no: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mobile_no: Mapped[str] = mapped_column(String(20), nullable=False)
    installment_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    contract_status: Mapped[str] = mapped_column(String(30), nullable=False, default="Active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    mappings: Mapped[list["LineMapping"]] = relationship(back_populates="contract", cascade="all, delete-orphan")
    payments: Mapped[list["PaymentSchedule"]] = relationship(back_populates="contract", cascade="all, delete-orphan")


class LineMapping(Base):
    __tablename__ = "line_mappings"
    __table_args__ = (
        UniqueConstraint("line_user_id", "map_status", name="uq_line_user_active_status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    contract_no: Mapped[str] = mapped_column(ForeignKey("contracts.contract_no"), nullable=False, index=True)
    customer_id: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    line_user_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    line_display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    map_status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    verified_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    mapped_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    unmapped_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_by: Mapped[str] = mapped_column(String(50), nullable=False, default="system")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    contract: Mapped[Contract] = relationship(back_populates="mappings")


class PaymentSchedule(Base):
    __tablename__ = "payment_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    contract_no: Mapped[str] = mapped_column(ForeignKey("contracts.contract_no"), nullable=False, index=True)
    installment_no: Mapped[int] = mapped_column(Integer, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=Decimal("0.00"))
    outstanding_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    payment_status: Mapped[str] = mapped_column(String(20), nullable=False)
    payment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    receipt_no: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    contract: Mapped[Contract] = relationship(back_populates="payments")


class ApiLog(Base):
    __tablename__ = "api_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    api_name: Mapped[str] = mapped_column(String(100), nullable=False)
    request_ref: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    contract_no: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)
    line_user_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    request_payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_code: Mapped[str] = mapped_column(String(30), nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
