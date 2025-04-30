from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel,Field



class AuthForm(BaseModel):
    identifier: str
    password: str
    device: Optional[str] = "unknown"
    ip_address: Optional[str] = "unknown"
    remember_me: Optional[bool] = Field(False)

class SessionSchema(BaseModel):
    user_id: int
    access_token: str
    refresh_token: str|None = Field(None)
    device: str = Field("unknown")
    ip_address: str = Field("unknown")

class SessionDTO(BaseModel):
    session_id: str
    user_id: int
    access_token: str
    refresh_token: str | None = None
    device: str = Field("unknown")
    ip_address: str = Field("unknown")
    created_at: datetime = Field(datetime.now())
    expires_at: datetime = Field(datetime.now())

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),  # Преобразование datetime в ISO строку
        }

class TokenModelResponse(BaseModel):
    token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    session_id: Optional[str] = None

class AccessTokenUpdate(BaseModel):
    old_access_token: str
    new_access_token: str

class AuthResponse(BaseModel):
    token: str
    data: Any = None