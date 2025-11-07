# backend/models.py
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

class SessionStartPayload(BaseModel):
    browser_name: str
    browser_version: str
    platform: str
    timezone: str

class SessionResponse(BaseModel):
    sid: int

class TabPayload(BaseModel):
    session_id: int
    user_id: Optional[int] = None  # Not needed - backend gets it from JWT token
    url: str
    title: Optional[str] = None

class TabResponse(BaseModel):
    tid: int
    domain_id: int

class ActivityEvent(BaseModel):
    tab_id: int # Extension must know this
    event_type: str
    timestamp: datetime
    url: Optional[str] = None
    mouse_x: Optional[int] = None
    mouse_y: Optional[int] = None
    scroll_y_pixels: Optional[int] = None
    scroll_y_percent: Optional[float] = None
    target_element_id: Optional[str] = None

class EventBatchPayload(BaseModel):
    session_id: int
    user_id: Optional[int] = None  # Not needed - backend gets it from JWT token
    events: List[ActivityEvent]

# Authentication Models
class UserLogin(BaseModel):
    email: str  # Allow both email and admin username
    password: str

class UserSignup(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str

class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    email: str