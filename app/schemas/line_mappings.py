from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LineMappingCreateRequest(BaseModel):
    contract_no: str = Field(..., examples=["EV0001"])
    line_user_id: str = Field(..., examples=["U1234567890"])
    line_display_name: str | None = Field(default=None, examples=["Alisa"])
    line_picture_url: str | None = Field(default=None, examples=["https://profile.line-scdn.net/xxx"])
    created_by: str = Field(default="system", examples=["system", "admin", "batch"])
    remark: str | None = Field(default=None, examples=["Mapped from LINE OA flow"])

    model_config = ConfigDict(from_attributes=True)


class LineMappingResponse(BaseModel):
    id: int
    contract_no: str
    customer_id: str
    line_user_id: str
    line_display_name: str | None = None
    line_picture_url: str | None = None

    map_status: str
    verified_flag: bool

    mapped_at: datetime
    unmapped_at: datetime | None = None

    created_by: str
    remark: str | None = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LineUnmapRequest(BaseModel):
    line_user_id: str = Field(..., examples=["U1234567890"])
    contract_no: str | None = Field(default=None, examples=["EV0001"])
    remark: str | None = Field(default=None, examples=["Change device / remap user"])

    model_config = ConfigDict(from_attributes=True)


class LineUnmapResponse(BaseModel):
    success: bool
    line_user_id: str
    contract_no: str | None = None
    map_status: str | None = None
    unmapped_at: datetime | None = None
    message: str

    model_config = ConfigDict(from_attributes=True)