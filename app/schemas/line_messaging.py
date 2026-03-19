from pydantic import BaseModel


class LinePushTextRequest(BaseModel):
    line_user_id: str
    text: str


class LinePushMenuRequest(BaseModel):
    line_user_id: str