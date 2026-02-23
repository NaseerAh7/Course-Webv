import uuid
import os
import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from models.purchase import ProgressUpdate
from middleware.auth import get_current_user
from typing import List, Callable
from datetime import datetime, timezone

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
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

@router.get("/my-courses")
async def get_my_courses(current_user: dict = Depends(get_current_user)):
    """Get all courses purchased by the current user."""
    db = get_db()
    
    try:
        # Get user with purchased courses
        user_doc = await db.users.find_one({"id": current_user['sub']}, {"_id": 0})
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")
        
        purchased_course_ids = user_doc.get('purchased_courses', [])
        
        if not purchased_course_ids:
            return []
        
        # Get courses
        courses = await db.courses.find(
            {"id": {"$in": purchased_course_ids}},
            {"_id": 0}
        ).to_list(100)
        
        # Get progress for each course
        result = []
        for course in courses:
            progress = await db.user_progress.find_one(
                {"user_id": current_user['sub'], "course_id": course['id']},
                {"_id": 0}
            )
            
            course_data = {
                "id": course['id'],
                "title": course['title'],
                "description": course.get('description', ''),
                "thumbnail_url": course.get('thumbnail_url'),
                "lessons_count": len(course.get('lessons', [])),
                "duration_hours": course.get('duration_hours', 0),
                "progress": progress.get('progress_percentage', 0.0) if progress else 0.0,
                "completed_lessons": progress.get('completed_lessons', []) if progress else [],
                "last_lesson_id": progress.get('last_lesson_id') if progress else None
            }
            result.append(course_data)
        
        logger.info(f"Retrieved {len(result)} courses for user {current_user['sub']}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user courses: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve courses")

@router.get("/course/{course_id}")
async def get_course_content(course_id: str, current_user: dict = Depends(get_current_user)):
    """Get full course content for a purchased course."""
    db = get_db()
    
    try:
        # Verify user has purchased the course
        user_doc = await db.users.find_one({"id": current_user['sub']}, {"_id": 0})
        if not user_doc or course_id not in user_doc.get('purchased_courses', []):
            raise HTTPException(status_code=403, detail="You have not purchased this course")
        
        # Get course
        course = await db.courses.find_one({"id": course_id}, {"_id": 0})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Get progress
        progress = await db.user_progress.find_one(
            {"user_id": current_user['sub'], "course_id": course_id},
            {"_id": 0}
        )
        
        return {
            "course": course,
            "progress": progress if progress else {
                "completed_lessons": [],
                "progress_percentage": 0.0
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get course content: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve course content")

@router.post("/course/{course_id}/progress")
async def update_progress(
    course_id: str,
    progress_data: ProgressUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update lesson completion progress."""
    db = get_db()
    
    try:
        # Verify user has purchased the course
        user_doc = await db.users.find_one({"id": current_user['sub']}, {"_id": 0})
        if not user_doc or course_id not in user_doc.get('purchased_courses', []):
            raise HTTPException(status_code=403, detail="You have not purchased this course")
        
        # Get course for lesson count
        course = await db.courses.find_one({"id": course_id}, {"_id": 0})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        total_lessons = len(course.get('lessons', []))
        
        # Get or create progress
        progress = await db.user_progress.find_one(
            {"user_id": current_user['sub'], "course_id": course_id},
            {"_id": 0}
        )
        
        if progress:
            completed_lessons = set(progress.get('completed_lessons', []))
            if progress_data.completed:
                completed_lessons.add(progress_data.lesson_id)
            else:
                completed_lessons.discard(progress_data.lesson_id)
            
            completed_lessons = list(completed_lessons)
            progress_percentage = (len(completed_lessons) / total_lessons * 100) if total_lessons > 0 else 0
            
            try:
                await db.user_progress.update_one(
                    {"user_id": current_user['sub'], "course_id": course_id},
                    {"$set": {
                        "completed_lessons": completed_lessons,
                        "last_lesson_id": progress_data.lesson_id,
                        "progress_percentage": progress_percentage,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
            except Exception as db_error:
                logger.error(f"Failed to update progress: {db_error}", exc_info=True)
                raise HTTPException(status_code=500, detail="Failed to update progress")
        else:
            completed_lessons = [progress_data.lesson_id] if progress_data.completed else []
            progress_percentage = (len(completed_lessons) / total_lessons * 100) if total_lessons > 0 else 0
            
            progress_doc = {
                "id": str(uuid.uuid4()),
                "user_id": current_user['sub'],
                "course_id": course_id,
                "completed_lessons": completed_lessons,
                "last_lesson_id": progress_data.lesson_id,
                "progress_percentage": progress_percentage,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            try:
                await db.user_progress.insert_one(progress_doc)
            except Exception as db_error:
                logger.error(f"Failed to create progress: {db_error}", exc_info=True)
                raise HTTPException(status_code=500, detail="Failed to create progress")
        
        logger.info(f"Progress updated for user {current_user['sub']}, course {course_id}")
        return {"message": "Progress updated", "progress_percentage": progress_percentage}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Progress update error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update progress")

@router.get("/course/{course_id}/pdf/{pdf_index}")
async def download_pdf(
    course_id: str,
    pdf_index: int,
    current_user: dict = Depends(get_current_user)
):
    """Download a PDF from a purchased course."""
    db = get_db()
    
    try:
        # Verify user has purchased the course
        user_doc = await db.users.find_one({"id": current_user['sub']}, {"_id": 0})
        if not user_doc or course_id not in user_doc.get('purchased_courses', []):
            raise HTTPException(status_code=403, detail="You have not purchased this course")
        
        # Get course
        course = await db.courses.find_one({"id": course_id}, {"_id": 0})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        pdf_materials = course.get('pdf_materials', [])
        if pdf_index < 0 or pdf_index >= len(pdf_materials):
            raise HTTPException(status_code=404, detail="PDF not found")
        
        pdf_path = pdf_materials[pdf_index]
        
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found on disk: {pdf_path}")
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        filename = os.path.basename(pdf_path)
        logger.info(f"User {current_user['sub']} downloading PDF: {filename}")
        return FileResponse(pdf_path, filename=filename, media_type="application/pdf")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF download error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to download PDF")
