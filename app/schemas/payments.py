from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PaymentScheduleCreateRequest(BaseModel):
    contract_no: str = Field(..., examples=["EV0001"])
    billing_seq: int = Field(..., examples=[1])
    billing_date: date = Field(..., examples=["2026-03-05"])

    daily_rent_amount: Decimal = Field(..., examples=["500.00"])
    paid_amount: Decimal = Field(default=Decimal("0.00"), examples=["0.00"])
    outstanding_amount: Decimal = Field(..., examples=["500.00"])

    payment_status: str = Field(default="UNPAID", examples=["UNPAID", "PARTIAL", "PAID"])
    payment_date: date | None = Field(default=None, examples=["2026-03-05"])
    receipt_no: str | None = Field(default=None, examples=["RC202603050001"])

    sent_line_flag: bool = Field(default=False)
    sent_line_at: datetime | None = Field(default=None)

    remark: str | None = Field(default=None, examples=["Initial billing schedule"])

    model_config = ConfigDict(from_attributes=True)


class PaymentReceiveRequest(BaseModel):
    contract_no: str = Field(..., examples=["EV0001"])
    billing_seq: int = Field(..., examples=[1])
    paid_amount: Decimal = Field(..., examples=["500.00"])
    payment_date: date = Field(..., examples=["2026-03-05"])
    receipt_no: str | None = Field(default=None, examples=["RC202603050001"])
    remark: str | None = Field(default=None, examples=["Paid at counter"])

    model_config = ConfigDict(from_attributes=True)


class PaymentScheduleResponse(BaseModel):
    id: int
    contract_no: str

    billing_seq: int
    billing_date: date

    daily_rent_amount: Decimal
    paid_amount: Decimal
    outstanding_amount: Decimal

    payment_status: str
    payment_date: date | None = None
    receipt_no: str | None = None

    sent_line_flag: bool
    sent_line_at: datetime | None = None

    remark: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentInquiryResponse(BaseModel):
    contract_no: str
    customer_name: str
    billing_seq: int
    billing_date: date
    daily_rent_amount: Decimal
    paid_amount: Decimal
    outstanding_amount: Decimal
    payment_status: str
    payment_date: date | None = None
    receipt_no: str | None = None
    remark: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PaymentHistoryItemResponse(BaseModel):
    contract_no: str
    billing_seq: int
    billing_date: date
    daily_rent_amount: Decimal
    paid_amount: Decimal
    outstanding_amount: Decimal
    payment_status: str
    payment_date: date | None = None
    receipt_no: str | None = None
    sent_line_flag: bool | None = None
    sent_line_at: datetime | None = None
    remark: str | None = None

    model_config = ConfigDict(from_attributes=True)