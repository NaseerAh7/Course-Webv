import uuid
import os
import shutil
import logging
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from models.course import CourseCreate, CourseUpdate, CourseInDB, CourseResponse, CourseListResponse, Lesson
from middleware.auth import get_current_user, require_admin, get_optional_user
from typing import List, Optional, Callable
from datetime import datetime, timezone

router = APIRouter(prefix="/courses", tags=["Courses"])
logger = logging.getLogger(__name__)

# Database dependency
db_dependency: Callable = None

def set_db_dependency(dep: Callable):
    global db_dependency
    db_dependency = dep

def get_db():
    if db_dependency is None:
        logger.error("Database dependency not configured")
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
    """List all published courses with optional filters."""
    db = get_db()
    
    try:
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
        
        logger.info(f"Listed {len(result)} courses")
        return result
        
    except Exception as e:
        logger.error(f"Failed to list courses: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve courses")

@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: str, user: Optional[dict] = Depends(get_optional_user)):
    """Get course details by ID."""
    db = get_db()
    
    try:
        course = await db.courses.find_one({"id": course_id}, {"_id": 0})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Parse datetime
        if isinstance(course.get('created_at'), str):
            course['created_at'] = datetime.fromisoformat(course['created_at'])
        if isinstance(course.get('updated_at'), str):
            course['updated_at'] = datetime.fromisoformat(course['updated_at'])
        
        return CourseResponse(**course)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get course {course_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve course")

@router.post("/", response_model=CourseResponse)
async def create_course(course_data: CourseCreate, admin: dict = Depends(require_admin)):
    """Create a new course (admin only)."""
    db = get_db()
    
    try:
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
        
        try:
            await db.courses.insert_one(course_dict)
            logger.info(f"Course created: {course.title} by {admin['email']}")
        except Exception as db_error:
            logger.error(f"Failed to insert course: {db_error}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to create course")
        
        return course
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Course creation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create course")

@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(course_id: str, updates: CourseUpdate, admin: dict = Depends(require_admin)):
    """Update a course (admin only)."""
    db = get_db()
    
    try:
        course = await db.courses.find_one({"id": course_id}, {"_id": 0})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        update_data = updates.model_dump(exclude_unset=True)
        update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
        
        try:
            await db.courses.update_one({"id": course_id}, {"$set": update_data})
            logger.info(f"Course updated: {course_id} by {admin['email']}")
        except Exception as db_error:
            logger.error(f"Failed to update course: {db_error}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to update course")
        
        updated_course = await db.courses.find_one({"id": course_id}, {"_id": 0})
        
        if isinstance(updated_course.get('created_at'), str):
            updated_course['created_at'] = datetime.fromisoformat(updated_course['created_at'])
        if isinstance(updated_course.get('updated_at'), str):
            updated_course['updated_at'] = datetime.fromisoformat(updated_course['updated_at'])
        
        return CourseResponse(**updated_course)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Course update error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update course")

@router.delete("/{course_id}")
async def delete_course(course_id: str, admin: dict = Depends(require_admin)):
    """Delete a course (admin only)."""
    db = get_db()
    
    try:
        result = await db.courses.delete_one({"id": course_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Course not found")
        
        logger.info(f"Course deleted: {course_id} by {admin['email']}")
        return {"message": "Course deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Course deletion error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete course")

@router.post("/{course_id}/lessons")
async def add_lesson(
    course_id: str,
    title: str = Form(...),
    description: str = Form(""),
    video_url: str = Form(...),
    duration_minutes: int = Form(0),
    admin: dict = Depends(require_admin)
):
    """Add a lesson to a course (admin only)."""
    db = get_db()
    
    try:
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
        
        try:
            await db.courses.update_one(
                {"id": course_id},
                {
                    "$push": {"lessons": lesson.model_dump()},
                    "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
                }
            )
            logger.info(f"Lesson added to course {course_id}: {title}")
        except Exception as db_error:
            logger.error(f"Failed to add lesson: {db_error}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to add lesson")
        
        return {"message": "Lesson added successfully", "lesson": lesson}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add lesson error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to add lesson")

@router.post("/{course_id}/pdf")
async def upload_pdf(
    course_id: str,
    file: UploadFile = File(...),
    admin: dict = Depends(require_admin)
):
    """Upload a PDF to a course (admin only)."""
    db = get_db()
    
    try:
        course = await db.courses.find_one({"id": course_id}, {"_id": 0})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Sanitize filename
        safe_filename = "".join(c for c in file.filename if c.isalnum() or c in '._-')
        
        # Save file
        file_id = str(uuid.uuid4())
        file_path = f"{UPLOAD_DIR}/{file_id}_{safe_filename}"
        
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as file_error:
            logger.error(f"Failed to save PDF: {file_error}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to save file")
        
        # Update course
        try:
            await db.courses.update_one(
                {"id": course_id},
                {
                    "$push": {"pdf_materials": file_path},
                    "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
                }
            )
            logger.info(f"PDF uploaded to course {course_id}: {safe_filename}")
        except Exception as db_error:
            logger.error(f"Failed to update course with PDF: {db_error}", exc_info=True)
            # Clean up uploaded file
            try:
                os.remove(file_path)
            except:
                pass
            raise HTTPException(status_code=500, detail="Failed to update course")
        
        return {"message": "PDF uploaded successfully", "file_path": file_path}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF upload error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to upload PDF")

@router.get("/admin/all", response_model=List[CourseListResponse])
async def list_all_courses_admin(admin: dict = Depends(require_admin)):
    """List all courses including unpublished (admin only)."""
    db = get_db()
    
    try:
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
        
    except Exception as e:
        logger.error(f"Failed to list admin courses: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve courses")
