from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CustomerVerifyRequest(BaseModel):
    contract_no: str = Field(..., examples=["EV0001"])
    id_card_no: str = Field(..., examples=["1103700000011"])
    mobile_no: str = Field(..., examples=["0811111111"])
    line_user_id: str | None = Field(default=None, examples=["U1234567890"])

    model_config = ConfigDict(from_attributes=True)


class CustomerVerifyResponse(BaseModel):
    verified: bool
    contract_no: str
    customer_id: str | None = None
    customer_name: str | None = None
    mobile_no: str | None = None

    vehicle_no: str | None = None
    vehicle_type: str | None = None

    contract_status: str | None = None
    contract_start_date: date | None = None
    contract_end_date: date | None = None

    total_paid_amount: Decimal | None = None
    total_outstanding_amount: Decimal | None = None
    last_payment_date: date | None = None

    line_notify_enabled: bool | None = None
    eligible_to_map: bool
    message: str

    model_config = ConfigDict(from_attributes=True)