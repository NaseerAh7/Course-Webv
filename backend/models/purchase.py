from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, List
from datetime import datetime, timezone
import uuid

class PurchaseCreate(BaseModel):
    course_id: str

class PurchaseInDB(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    course_id: str
    amount: float = Field(ge=0)
    currency: str = Field(default="usd", pattern="^[a-z]{3}$")
    payment_session_id: str
    payment_status: str = Field(default="pending", pattern="^(pending|paid|failed|refunded|expired)$")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PaymentTransactionInDB(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_email: str
    course_id: str
    amount: float = Field(ge=0)
    currency: str = Field(default="usd", pattern="^[a-z]{3}$")
    session_id: str
    payment_status: str = Field(default="initiated", pattern="^(initiated|pending|paid|failed|expired)$")
    metadata: Dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserProgress(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    course_id: str
    completed_lessons: List[str] = Field(default_factory=list)
    last_lesson_id: Optional[str] = None
    progress_percentage: float = Field(default=0.0, ge=0, le=100)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProgressUpdate(BaseModel):
    lesson_id: str
    completed: bool = True
