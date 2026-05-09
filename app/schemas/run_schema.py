from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.user_schema import UserOut


class UserRunRoutePointCreate(BaseModel):
    sequence_index: int = Field(ge=0)
    latitude: float
    longitude: float
    elapsed_time_millis: int = Field(ge=0)
    distance_meters: float = Field(ge=0)


class UserRunCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    performed_at_millis: int = Field(gt=0)
    duration_millis: int = Field(ge=0)
    distance_km: float = Field(ge=0)
    avg_speed_kmh: float = Field(ge=0)
    max_speed_kmh: float = Field(ge=0)
    pace_min_per_km: float = Field(ge=0)
    route_points: list[UserRunRoutePointCreate] = Field(default_factory=list)


class UserRunRoutePointResponse(BaseModel):
    sequence_index: int
    latitude: float
    longitude: float
    elapsed_time_millis: int
    distance_meters: float

    class Config:
        from_attributes = True


class UserRunResponse(BaseModel):
    id: int
    user_id: int
    name: str
    performed_at: datetime
    duration_millis: int
    distance_km: float
    avg_speed_kmh: float
    max_speed_kmh: float
    pace_min_per_km: float
    is_shared: bool
    share_code: str
    route_points: list[UserRunRoutePointResponse] = Field(default_factory=list)
    owner: UserOut | None = None

    class Config:
        from_attributes = True


class UserRunShareResponse(BaseModel):
    run_id: int
    is_shared: bool
    share_code: str
