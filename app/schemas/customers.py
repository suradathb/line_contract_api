from pydantic import BaseModel, Field


class CustomerVerifyRequest(BaseModel):
    contract_no: str = Field(..., examples=["EV0001"])
    line_user_id: str = Field(..., examples=["U1234567890"])
    # id_card_no: str = Field(..., examples=["1103700000011"])
    # mobile_no: str = Field(..., examples=["0811111111"])


class CustomerVerifyResponse(BaseModel):
    verified: bool
    contract_no: str
    customer_name: str | None = None
    contract_status: str | None = None
    eligible_to_map: bool
    message: str
