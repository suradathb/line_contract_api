from datetime import datetime

from pydantic import BaseModel, Field


class LineMappingCreateRequest(BaseModel):
    contract_no: str = Field(..., examples=["EV0001"])
    line_user_id: str = Field(..., examples=["U1234567890"])
    line_display_name: str | None = Field(default=None, examples=["Alisa"])
    created_by: str = Field(default="system")


class LineMappingResponse(BaseModel):
    mapping_id: int
    contract_no: str
    customer_id: str
    line_user_id: str
    line_display_name: str | None
    map_status: str
    verified_flag: bool
    mapped_at: datetime


class LineUnmapRequest(BaseModel):
    line_user_id: str = Field(..., examples=["U1234567890"])
    reason: str | None = Field(default=None, examples=["Change device"])


class LineUnmapResponse(BaseModel):
    success: bool
    line_user_id: str
    contract_no: str | None = None
    message: str
