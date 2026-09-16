from pydantic import BaseModel, EmailStr


class LoginDto(BaseModel):
    email: EmailStr
    password: str


class TokenResponseDto(BaseModel):
    access_token: str
    token_type: str = "bearer"