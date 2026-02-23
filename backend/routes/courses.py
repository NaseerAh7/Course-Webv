from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from models.course import CourseCreate, CourseUpdate, CourseInDB, CourseResponse, CourseListResponse, Lesson
from middleware.auth import get_current_user, require_admin, get_optional_user
from typing import List, Optional, Callable
from datetime import datetime, timezone
import os
import uuid
import shutil

router = APIRouter(prefix="/courses", tags=["Courses"])

# Database dependency
db_dependency: Callable = None

def set_db_dependency(dep: Callable):
    global db_dependency
    db_dependency = dep

def get_db():
    if db_dependency is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    return db_dependency()

# Ensure uploads directory exists
UPLOAD_DIR = "/app/backend/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/", response_model=List[CourseListResponse])
async def list_courses(
    category: Optional[str] = None,
    level: Optional[str] = None,
    search: Optional[str] = None
):
    db = get_db()
    
    query = {"is_published": True}
    if category:
        query["category"] = category
    if level:
        query["level"] = level
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    courses = await db.courses.find(query, {"_id": 0}).to_list(100)
    
    result = []
    for course in courses:
        result.append(CourseListResponse(
            id=course['id'],
            title=course['title'],
            short_description=course.get('short_description', ''),
            price=course['price'],
            thumbnail_url=course.get('thumbnail_url'),
            category=course.get('category', 'General'),
            level=course.get('level', 'Beginner'),
            duration_hours=course.get('duration_hours', 0),
            instructor_name=course.get('instructor_name', ''),
            enrolled_count=course.get('enrolled_count', 0),
            rating=course.get('rating', 0.0),
            lessons_count=len(course.get('lessons', []))
        ))
    
    return result

@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: str, user: Optional[dict] = Depends(get_optional_user)):
    db = get_db()
    
    course = await db.courses.find_one({"id": course_id}, {"_id": 0})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Parse datetime
    if isinstance(course.get('created_at'), str):
        course['created_at'] = datetime.fromisoformat(course['created_at'])
    if isinstance(course.get('updated_at'), str):
        course['updated_at'] = datetime.fromisoformat(course['updated_at'])
    
    return CourseResponse(**course)

@router.post("/", response_model=CourseResponse)
async def create_course(course_data: CourseCreate, admin: dict = Depends(require_admin)):
    db = get_db()
    
    # Create lessons with IDs
    lessons = [Lesson(**lesson.model_dump()) for lesson in course_data.lessons]
    
    course = CourseInDB(
        **course_data.model_dump(exclude={'lessons'}),
        lessons=lessons,
        instructor_id=admin['sub'],
        instructor_name=admin['name']
    )
    
    course_dict = course.model_dump()
    course_dict['created_at'] = course_dict['created_at'].isoformat()
    course_dict['updated_at'] = course_dict['updated_at'].isoformat()
    
    await db.courses.insert_one(course_dict)
    
    return course

@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(course_id: str, updates: CourseUpdate, admin: dict = Depends(require_admin)):
    db = get_db()
    
    course = await db.courses.find_one({"id": course_id}, {"_id": 0})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    update_data = updates.model_dump(exclude_unset=True)
    update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    await db.courses.update_one({"id": course_id}, {"$set": update_data})
    
    updated_course = await db.courses.find_one({"id": course_id}, {"_id": 0})
    
    if isinstance(updated_course.get('created_at'), str):
        updated_course['created_at'] = datetime.fromisoformat(updated_course['created_at'])
    if isinstance(updated_course.get('updated_at'), str):
        updated_course['updated_at'] = datetime.fromisoformat(updated_course['updated_at'])
    
    return CourseResponse(**updated_course)

@router.delete("/{course_id}")
async def delete_course(course_id: str, admin: dict = Depends(require_admin)):
    db = get_db()
    
    result = await db.courses.delete_one({"id": course_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return {"message": "Course deleted successfully"}

@router.post("/{course_id}/lessons")
async def add_lesson(
    course_id: str,
    title: str = Form(...),
    description: str = Form(""),
    video_url: str = Form(...),
    duration_minutes: int = Form(0),
    admin: dict = Depends(require_admin)
):
    db = get_db()
    
    course = await db.courses.find_one({"id": course_id}, {"_id": 0})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    lesson = Lesson(
        title=title,
        description=description,
        video_url=video_url,
        duration_minutes=duration_minutes,
        order=len(course.get('lessons', []))
    )
    
    await db.courses.update_one(
        {"id": course_id},
        {
            "$push": {"lessons": lesson.model_dump()},
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )
    
    return {"message": "Lesson added successfully", "lesson": lesson}

@router.post("/{course_id}/pdf")
async def upload_pdf(
    course_id: str,
    file: UploadFile = File(...),
    admin: dict = Depends(require_admin)
):
    db = get_db()
    
    course = await db.courses.find_one({"id": course_id}, {"_id": 0})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Save file
    file_id = str(uuid.uuid4())
    file_path = f"{UPLOAD_DIR}/{file_id}_{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update course
    await db.courses.update_one(
        {"id": course_id},
        {
            "$push": {"pdf_materials": file_path},
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )
    
    return {"message": "PDF uploaded successfully", "file_path": file_path}

@router.get("/admin/all", response_model=List[CourseListResponse])
async def list_all_courses_admin(admin: dict = Depends(require_admin)):
    db = get_db()
    
    courses = await db.courses.find({}, {"_id": 0}).to_list(100)
    
    result = []
    for course in courses:
        result.append(CourseListResponse(
            id=course['id'],
            title=course['title'],
            short_description=course.get('short_description', ''),
            price=course['price'],
            thumbnail_url=course.get('thumbnail_url'),
            category=course.get('category', 'General'),
            level=course.get('level', 'Beginner'),
            duration_hours=course.get('duration_hours', 0),
            instructor_name=course.get('instructor_name', ''),
            enrolled_count=course.get('enrolled_count', 0),
            rating=course.get('rating', 0.0),
            lessons_count=len(course.get('lessons', []))
        ))
    
    return result
