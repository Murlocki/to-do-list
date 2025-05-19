from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field, EmailStr, AliasChoices
from pydantic.alias_generators import to_camel

from src.shared.models import TaskStatus


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

class AccessTokenUpdate(BaseModel):
    old_access_token: str
    new_access_token: str

class AuthResponse(BaseModel):
    token: str
    data: Any = None

class UserDTO(BaseModel):
    id: int
    username: str = Field(validation_alias=AliasChoices('username', 'userName'))
    first_name: str = Field(validation_alias=AliasChoices('first_name', 'firstName'))
    last_name: str = Field(validation_alias=AliasChoices('last_name', 'lastName'))
    email: EmailStr
    is_active: bool = Field(False, validation_alias=AliasChoices('is_active', 'isActive'))
    is_superuser: bool = Field(False, validation_alias=AliasChoices('is_superuser', 'isSuperuser'))
    version: int = Field(0)
    class Config:
        alias_generator = to_camel
        from_attributes = True
class UserAuthDTO(BaseModel):
    identifier: str
    password: str
class PasswordForm(BaseModel):
    new_password: str

class TaskDTO(BaseModel):
    id: int
    title: str
    description: str | None = Field(None)
    status: int = Field(TaskStatus.IN_PROGRESS.value)
    user_id: int = Field(validation_alias=AliasChoices('user_id', 'userId'))
    fulfilled_date: Optional[datetime] | None = Field(None,validation_alias=AliasChoices('fulfilled_date', 'fulfilledDate'))
    version: int = Field(0)
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),  # Преобразование datetime в ISO строку
        }
        alias_generator = to_camel
        validate_by_name = True