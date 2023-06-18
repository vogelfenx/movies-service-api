from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class UserToken(BaseModel):
    username: str
    roles: list[str] = Field(default_factory=list)
