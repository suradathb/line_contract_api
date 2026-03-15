from pydantic import BaseModel, ConfigDict


class MessageResponse(BaseModel):
    message: str

    model_config = ConfigDict(from_attributes=True)


class SuccessResponse(BaseModel):
    success: bool
    message: str

    model_config = ConfigDict(from_attributes=True)