from pydantic import BaseModel


class ExecuteActionRequest(BaseModel):
    action: str
    params: dict = {}


class ExecuteActionResponse(BaseModel):
    action: str
    status: str  # acknowledged | rejected
    message: str
