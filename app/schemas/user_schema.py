from pydantic import BaseModel, Field


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    nickname: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=4, max_length=255)


class UserLogin(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=4, max_length=255)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: int
    username: str
    nickname: str
    avatar_url: str | None = None

    class Config:
        from_attributes = True


class UserOut(BaseModel):
    id: int
    username: str
    nickname: str
    avatar_url: str | None = None

    class Config:
        from_attributes = True


class UpdateNicknameRequest(BaseModel):
    nickname: str = Field(min_length=1, max_length=100)


class ChangePasswordRequest(BaseModel):
    new_password: str = Field(min_length=1, max_length=255)


class ApiMessageResponse(BaseModel):
    message: str


class LeaderboardEntryResponse(BaseModel):
    rank: int
    user: UserResponse
    total_distance_km: float
    total_runs: int
    average_pace_min_per_km: float | None = None
