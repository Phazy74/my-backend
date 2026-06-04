from pydantic import BaseModel, EmailStr
from typing import Optional


# ── User schemas ──────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str

    model_config = {"from_attributes": True}


# ── Token schemas ─────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# ── Item schemas ──────────────────────────────────────────────

class ItemCreate(BaseModel):
    title: str
    description: Optional[str] = None


class ItemOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    owner_id: int

    model_config = {"from_attributes": True}
