from pydantic import BaseModel, EmailStr, Field


class LoginDto(BaseModel):
    email: EmailStr
    password: str


class TokenResponseDto(BaseModel):
    access_token: str
    refresh_token: str

    token_type: str = "bearer"


class RefreshTokenDto(BaseModel):
    refresh_token: str = Field(
        min_length=20,
    )