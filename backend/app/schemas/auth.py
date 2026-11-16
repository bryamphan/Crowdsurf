"""Request and response shapes for host signup and login."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class HostSignup(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, v: str) -> str:
        return v.lower()  # so Bob@x.com and bob@x.com are the same account

    @field_validator("password")
    @classmethod
    def fits_bcrypt(cls, v: str) -> str:
        if len(v.encode()) > 72:
            raise ValueError("Password is too long (max 72 bytes)")
        return v


class HostLogin(BaseModel):
    # No length rules here: a wrong password should get "incorrect", not a 422.
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, v: str) -> str:
        return v.lower()


class HostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # lets us return a Host model directly

    id: int
    email: str
    created_at: datetime


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    host: HostOut
