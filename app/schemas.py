# schemas.py
# Description: Pydantic models for the auth service.

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []


class User(BaseModel):
    username: str
    email: EmailStr = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInCreate(User):
    password: str


class UserInDB(User):
    hashed_password: str


class UserInResponse(UserInDB):
    id: int
