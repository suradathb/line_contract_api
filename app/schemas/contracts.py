from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ContractBase(BaseModel):
    contract_no: str = Field(..., examples=["EV0001"])
    customer_id: str = Field(..., examples=["CUST0001"])
    id_card_no: str = Field(..., examples=["1103700000011"])
    customer_name: str = Field(..., examples=["Somchai Jaidee"])
    mobile_no: str = Field(..., examples=["0811111111"])

    vehicle_no: str | None = Field(default=None, examples=["1กข1234"])
    vehicle_type: str | None = Field(default=None, examples=["Taxi", "Sedan"])

    daily_rent_amount: Decimal = Field(..., examples=["500.00"])
    deposit_amount: Decimal = Field(default=Decimal("0.00"), examples=["3000.00"])

    contract_start_date: date = Field(..., examples=["2026-03-01"])
    contract_end_date: date | None = Field(default=None, examples=["2026-12-31"])

    contract_status: str = Field(default="ACTIVE", examples=["ACTIVE", "CLOSED", "SUSPENDED"])
    line_notify_enabled: bool = Field(default=True)
    remark: str | None = Field(default=None, examples=["First contract"])


class ContractCreateRequest(ContractBase):
    total_paid_amount: Decimal = Field(default=Decimal("0.00"), examples=["0.00"])
    total_outstanding_amount: Decimal = Field(default=Decimal("0.00"), examples=["15000.00"])
    last_payment_date: date | None = Field(default=None, examples=["2026-03-10"])


class ContractUpdateRequest(BaseModel):
    customer_id: str | None = Field(default=None, examples=["CUST0001"])
    id_card_no: str | None = Field(default=None, examples=["1103700000011"])
    customer_name: str | None = Field(default=None, examples=["Somchai Jaidee"])
    mobile_no: str | None = Field(default=None, examples=["0811111111"])

    vehicle_no: str | None = Field(default=None, examples=["1กข1234"])
    vehicle_type: str | None = Field(default=None, examples=["Taxi"])

    daily_rent_amount: Decimal | None = Field(default=None, examples=["500.00"])
    deposit_amount: Decimal | None = Field(default=None, examples=["3000.00"])

    contract_start_date: date | None = Field(default=None, examples=["2026-03-01"])
    contract_end_date: date | None = Field(default=None, examples=["2026-12-31"])

    contract_status: str | None = Field(default=None, examples=["ACTIVE", "CLOSED", "SUSPENDED"])

    total_paid_amount: Decimal | None = Field(default=None, examples=["1000.00"])
    total_outstanding_amount: Decimal | None = Field(default=None, examples=["14000.00"])
    last_payment_date: date | None = Field(default=None, examples=["2026-03-10"])

    line_notify_enabled: bool | None = Field(default=None)
    remark: str | None = Field(default=None, examples=["Updated contract detail"])

    model_config = ConfigDict(from_attributes=True)


class ContractResponse(BaseModel):
    contract_no: str
    customer_id: str
    id_card_no: str
    customer_name: str
    mobile_no: str

    vehicle_no: str | None = None
    vehicle_type: str | None = None

    daily_rent_amount: Decimal
    deposit_amount: Decimal

    contract_start_date: date
    contract_end_date: date | None = None

    contract_status: str

    total_paid_amount: Decimal
    total_outstanding_amount: Decimal
    last_payment_date: date | None = None

    line_notify_enabled: bool
    remark: str | None = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)