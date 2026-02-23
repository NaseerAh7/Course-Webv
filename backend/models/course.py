from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
import uuid

class LessonBase(BaseModel):
    title: str
    description: Optional[str] = None
    video_url: str  # YouTube embed URL
    duration_minutes: int = 0
    order: int = 0

class LessonCreate(LessonBase):
    pass

class Lesson(LessonBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class CourseBase(BaseModel):
    title: str
    description: str
    short_description: str = ""
    price: float = Field(ge=0)
    thumbnail_url: Optional[str] = None
    category: str = "General"
    level: str = "Beginner"  # Beginner, Intermediate, Advanced
    duration_hours: int = 0

class CourseCreate(CourseBase):
    lessons: List[LessonCreate] = Field(default_factory=list)

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    price: Optional[float] = None
    thumbnail_url: Optional[str] = None
    category: Optional[str] = None
    level: Optional[str] = None
    duration_hours: Optional[int] = None
    is_published: Optional[bool] = None

class CourseInDB(CourseBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    lessons: List[Lesson] = Field(default_factory=list)
    pdf_materials: List[str] = Field(default_factory=list)  # List of PDF file paths
    instructor_id: str = ""
    instructor_name: str = ""
    is_published: bool = True
    enrolled_count: int = 0
    rating: float = 0.0
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
