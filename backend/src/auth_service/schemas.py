from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(None, min_length=3, max_length=50)
    first_name: str
    last_name: str
    email: EmailStr
    password: str = Field(min_length=8)
class UserUpdate(BaseModel):
    username: str = Field(None, min_length=3, max_length=50)
    first_name: str
    last_name: str
    email: EmailStr
    password: str = Field(min_length=8)
    is_active: bool = Field(True)
class AuthForm(BaseModel):
    identifier: str
    password: str
    device: Optional[str] = "unknown"
    ip_address: Optional[str] = "unknown"
    remember_me: Optional[bool] = Field(False)


