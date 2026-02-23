from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
import uuid

class LessonBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    video_url: str = Field(min_length=1)  # YouTube embed URL
    duration_minutes: int = Field(default=0, ge=0)
    order: int = Field(default=0, ge=0)

class LessonCreate(LessonBase):
    pass

class Lesson(LessonBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class CourseBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=5000)
    short_description: str = Field(default="", max_length=500)
    price: float = Field(ge=0, le=10000)
    thumbnail_url: Optional[str] = None
    category: str = Field(default="General", max_length=100)
    level: str = Field(default="Beginner", pattern="^(Beginner|Intermediate|Advanced)$")
    duration_hours: int = Field(default=0, ge=0)

class CourseCreate(CourseBase):
    lessons: List[LessonCreate] = Field(default_factory=list)

class CourseUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=5000)
    short_description: Optional[str] = Field(default=None, max_length=500)
    price: Optional[float] = Field(default=None, ge=0, le=10000)
    thumbnail_url: Optional[str] = None
    category: Optional[str] = Field(default=None, max_length=100)
    level: Optional[str] = Field(default=None, pattern="^(Beginner|Intermediate|Advanced)$")
    duration_hours: Optional[int] = Field(default=None, ge=0)
    is_published: Optional[bool] = None

class CourseInDB(CourseBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    lessons: List[Lesson] = Field(default_factory=list)
    pdf_materials: List[str] = Field(default_factory=list)
    instructor_id: str = ""
    instructor_name: str = ""
    is_published: bool = True
    enrolled_count: int = Field(default=0, ge=0)
    rating: float = Field(default=0.0, ge=0, le=5)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CourseResponse(CourseInDB):
    pass

class CourseListResponse(BaseModel):
    id: str
    title: str
    short_description: str
    price: float
    thumbnail_url: Optional[str]
    category: str
    level: str
    duration_hours: int
    instructor_name: str
    enrolled_count: int
    rating: float
    lessons_count: int
