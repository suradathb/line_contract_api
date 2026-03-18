from pydantic import BaseModel, Field
from decimal import Decimal


class CustomerVerifyRequest(BaseModel):
    contract_no: str = Field(..., examples=["EV0001"])
    line_user_id: str = Field(..., examples=["U1234567890"])


class CustomerVerifyResponse(BaseModel):
    verified: bool
    contract_no: str
    customer_name: str | None = None
    contract_status: str | None = None
    eligible_to_map: bool
    message: str

class CustomerUnmapRequest(BaseModel):
    contract_no: str

class CustomerUnmapResponse(BaseModel):
    success: bool
    contract_no: str
    message: str


class CustomerMapRequest(BaseModel):
    contract_no: str
    line_user_id: str
    line_display_name: str | None = None


class CustomerMapResponse(BaseModel):
    success: bool
    contract_no: str
    line_user_id: str
    line_display_name: str | None = None
    message: str

