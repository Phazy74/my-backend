from pydantic import BaseModel, EmailStr
from typing import Optional

# ── USER ─────────────────────────────

class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str

    model_config = {"from_attributes": True}


# ── TOKEN ────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str


# ── BOOKING ──────────────────────────

class BookingCreate(BaseModel):
    customer_name: str
    service_name: str
    booking_date: str
    notes: Optional[str] = None


class BookingOut(BaseModel):
    id: int
    customer_name: str
    service_name: str
    booking_date: str
    status: str
    notes: Optional[str]
    owner_id: int

    model_config = {"from_attributes": True}