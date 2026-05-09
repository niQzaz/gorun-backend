from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.user_schema import UserOut


class MessageCreate(BaseModel):
    conversation_id: int
    content: str | None = Field(default=None, max_length=4000)
    client_message_id: str | None = Field(default=None, max_length=64)
    message_type: str = Field(default="text", max_length=32)
    shared_run_code: str | None = Field(default=None, max_length=64)


class JointRunCreate(BaseModel):
    mode: str = Field(max_length=16)
    target_seconds: int | None = Field(default=None, ge=1)
    target_distance_meters: float | None = Field(default=None, gt=0)
    client_message_id: str | None = Field(default=None, max_length=64)


class JointRunLiveUpdate(BaseModel):
    latitude: float | None = None
    longitude: float | None = None
    distance_meters: float = Field(ge=0)
    duration_millis: int = Field(ge=0)
    max_speed_kmh: float | None = Field(default=None, ge=0)


class SharedRunPreview(BaseModel):
    share_code: str
    name: str
    distance_km: float
    duration_millis: int
    performed_at: datetime


class JointRunUserPreview(BaseModel):
    id: int
    username: str
    nickname: str
    avatar_url: str | None = None


class RoutePointPreview(BaseModel):
    sequence_index: int
    latitude: float
    longitude: float
    elapsed_time_millis: int
    distance_meters: float


class JointRunRouteResponse(BaseModel):
    challenge_id: int
    creator_id: int
    opponent_id: int
    creator_route: list[RoutePointPreview]
    opponent_route: list[RoutePointPreview]


class JointRunPreview(BaseModel):
    id: int
    conversation_id: int
    creator_id: int
    opponent_id: int
    mode: str
    target_seconds: int | None = None
    target_distance_meters: float | None = None
    status: str
    creator_ready: bool
    opponent_ready: bool
    creator_distance_meters: float
    opponent_distance_meters: float
    creator_duration_millis: int
    opponent_duration_millis: int
    creator_max_speed_kmh: float | None = None
    opponent_max_speed_kmh: float | None = None
    creator_latitude: float | None = None
    creator_longitude: float | None = None
    opponent_latitude: float | None = None
    opponent_longitude: float | None = None
    winner_id: int | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    creator: JointRunUserPreview | None = None
    opponent: JointRunUserPreview | None = None


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    content: str
    client_message_id: str | None = None
    message_type: str
    image_url: str | None = None
    shared_run: SharedRunPreview | None = None
    joint_run: JointRunPreview | None = None
    is_read: bool = False
    created_at: datetime


class ReadReceiptResponse(BaseModel):
    conversation_id: int
    message_ids: list[int]


class ConversationResponse(BaseModel):
    id: int
    user1_id: int
    user2_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ChatPreview(BaseModel):
    conversation_id: int
    user: UserOut
    last_message: str | None
    last_message_time: datetime | None

    class Config:
        from_attributes = True
