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
    first_name: str = Field(None)
    last_name: str = Field(None)
    email: EmailStr = Field(None)
    password: str = Field(None)
    is_active: bool = Field(True)
    is_admin: bool = Field(False)
class UserResponse(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    is_active: bool = Field(True)
    is_superuser: bool = Field(False)
    created_at: datetime = Field(datetime.now())
    updated_at: datetime = Field(datetime.now())
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),  # Преобразование datetime в ISO строку
        }

class TokenModelResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    session_id: Optional[str] = None
class TokenDTO(BaseModel):
    access_token: str
