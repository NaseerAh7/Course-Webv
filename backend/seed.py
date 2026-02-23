#!/usr/bin/env python3
"""
Seed Script for Course Platform
Creates admin user, demo student, and sample courses with lessons.
Run with: python seed.py
"""

import asyncio
import os
import sys
import uuid
from pathlib import Path
from datetime import datetime, timezone

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

load_dotenv(Path(__file__).parent / '.env')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ============================================================================
# DEMO DATA
# ============================================================================

ADMIN_USER = {
    "email": "admin@courseplatform.com",
    "password": "admin123",
    "name": "Admin User",
    "role": "admin"
}

DEMO_STUDENT = {
    "email": "student@demo.com",
    "password": "student123",
    "name": "Demo Student",
    "role": "student"
}

DEMO_COURSES = [
    {
        "title": "Complete Web Development Bootcamp 2024",
        "description": "Master web development from scratch! This comprehensive course covers HTML, CSS, JavaScript, React, Node.js, and MongoDB. Perfect for beginners who want to become full-stack developers. Learn through hands-on projects and real-world examples.",
        "short_description": "Learn full-stack web development from HTML basics to React and Node.js",
        "price": 49.99,
        "thumbnail_url": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=800",
        "category": "Web Development",
        "level": "Beginner",
        "duration_hours": 40,
        "rating": 4.8,
        "enrolled_count": 1247,
        "lessons": [
            {
                "title": "Introduction to Web Development",
                "description": "Learn what web development is and set up your development environment",
                "video_url": "https://www.youtube.com/embed/UB1O30fR-EE",
                "duration_minutes": 15,
                "order": 0
            },
            {
                "title": "HTML Fundamentals",
                "description": "Master HTML tags, structure, and semantic markup",
                "video_url": "https://www.youtube.com/embed/qz0aGYrrlhU",
                "duration_minutes": 45,
                "order": 1
            },
            {
                "title": "CSS Styling Basics",
                "description": "Learn CSS selectors, properties, and responsive design",
                "video_url": "https://www.youtube.com/embed/1PnVor36_40",
                "duration_minutes": 60,
                "order": 2
            },
            {
                "title": "JavaScript Essentials",
                "description": "Understand JavaScript fundamentals and DOM manipulation",
                "video_url": "https://www.youtube.com/embed/W6NZfCO5SIk",
                "duration_minutes": 90,
                "order": 3
            }
        ],
        "pdf_materials": []
    },
    {
        "title": "Python for Data Science & Machine Learning",
        "description": "Dive into the world of data science with Python! Learn NumPy, Pandas, Matplotlib, and scikit-learn to analyze data and build machine learning models. This course includes real datasets and practical projects.",
        "short_description": "Master Python for data analysis, visualization, and machine learning",
        "price": 79.99,
        "thumbnail_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800",
        "category": "Data Science",
        "level": "Intermediate",
        "duration_hours": 35,
        "rating": 4.9,
        "enrolled_count": 892,
        "lessons": [
            {
                "title": "Python Basics for Data Science",
                "description": "Review Python fundamentals with a focus on data science applications",
                "video_url": "https://www.youtube.com/embed/rfscVS0vtbw",
                "duration_minutes": 30,
                "order": 0
            },
            {
                "title": "NumPy for Numerical Computing",
                "description": "Master arrays, matrices, and numerical operations with NumPy",
                "video_url": "https://www.youtube.com/embed/QUT1VHiLmmI",
                "duration_minutes": 45,
                "order": 1
            },
            {
                "title": "Data Analysis with Pandas",
                "description": "Learn DataFrames, data cleaning, and analysis techniques",
                "video_url": "https://www.youtube.com/embed/vmEHCJofslg",
                "duration_minutes": 60,
                "order": 2
            }
        ],
        "pdf_materials": []
    },
    {
        "title": "UI/UX Design Masterclass",
        "description": "Learn the principles of great design! This course covers user research, wireframing, prototyping, and design systems using Figma. Build a portfolio of professional design projects.",
        "short_description": "Create stunning user interfaces and seamless user experiences",
        "price": 59.99,
        "thumbnail_url": "https://images.unsplash.com/photo-1561070791-2526d30994b5?w=800",
        "category": "Design",
        "level": "Beginner",
        "duration_hours": 25,
        "rating": 4.7,
        "enrolled_count": 634,
        "lessons": [
            {
                "title": "Introduction to UI/UX Design",
                "description": "Understand the difference between UI and UX and why both matter",
                "video_url": "https://www.youtube.com/embed/c9Wg6Cb_YlU",
                "duration_minutes": 20,
                "order": 0
            },
            {
                "title": "User Research Methods",
                "description": "Learn how to conduct interviews, surveys, and usability tests",
                "video_url": "https://www.youtube.com/embed/TpY1l2bKpAA",
                "duration_minutes": 35,
                "order": 1
            },
            {
                "title": "Wireframing and Prototyping",
                "description": "Create low-fidelity and high-fidelity prototypes in Figma",
                "video_url": "https://www.youtube.com/embed/FTFaQWZBqQ8",
                "duration_minutes": 50,
                "order": 2
            }
        ],
        "pdf_materials": []
    }
]

# ============================================================================
# SEED FUNCTIONS
# ============================================================================

async def create_user(db, user_data: dict, admin_id: str = None) -> str:
    """Create a user and return their ID."""
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    user_doc = {
        "id": user_id,
        "email": user_data["email"],
        "name": user_data["name"],
        "password_hash": pwd_context.hash(user_data["password"]),
        "role": user_data["role"],
        "purchased_courses": [],  # Empty - no purchased courses for demo users
        "created_at": now,
        "updated_at": now
    }
    
    try:
        await db.users.insert_one(user_doc)
        logger.info(f"✅ Created {user_data['role']}: {user_data['email']} / {user_data['password']}")
        return user_id
    except Exception as e:
        if "duplicate key" in str(e):
            existing = await db.users.find_one({"email": user_data["email"]})
            logger.info(f"ℹ️  {user_data['role'].capitalize()} already exists: {user_data['email']}")
            return existing["id"] if existing else user_id
        raise

async def create_course(db, course_data: dict, instructor_id: str, instructor_name: str) -> str:
    """Create a course with lessons and return its ID."""
    course_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    # Create lessons with IDs
    lessons = []
    for lesson in course_data.get("lessons", []):
        lessons.append({
            "id": str(uuid.uuid4()),
            **lesson
        })
    
    course_doc = {
        "id": course_id,
        "title": course_data["title"],
        "description": course_data["description"],
        "short_description": course_data["short_description"],
        "price": course_data["price"],
        "thumbnail_url": course_data["thumbnail_url"],
        "category": course_data["category"],
        "level": course_data["level"],
        "duration_hours": course_data["duration_hours"],
        "instructor_id": instructor_id,
        "instructor_name": instructor_name,
        "is_published": True,
        "enrolled_count": course_data.get("enrolled_count", 0),
        "rating": course_data.get("rating", 0.0),
        "lessons": lessons,
        "pdf_materials": course_data.get("pdf_materials", []),
        "created_at": now,
        "updated_at": now
    }
    
    try:
        await db.courses.insert_one(course_doc)
        logger.info(f"✅ Created course: {course_data['title']}")
        return course_id
    except Exception as e:
        if "duplicate key" in str(e):
            logger.info(f"ℹ️  Course already exists: {course_data['title']}")
            return course_id
        raise

async def create_indexes(db):
    """Create database indexes."""
    try:
        await db.users.create_index("email", unique=True)
        await db.users.create_index("id", unique=True)
        await db.courses.create_index("id", unique=True)
        await db.payment_transactions.create_index("session_id", unique=True)
        await db.user_progress.create_index([("user_id", 1), ("course_id", 1)])
        logger.info("✅ Database indexes created")
    except Exception as e:
        logger.warning(f"⚠️  Index creation warning (may already exist): {e}")

async def seed_database():
    """Main seed function."""
    # Validate environment
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    
    if not mongo_url or not db_name:
        logger.error("❌ MONGO_URL and DB_NAME must be set in .env")
        sys.exit(1)
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("🌱 Course Platform Database Seeder")
    logger.info("=" * 60)
    logger.info("")
    
    # Connect to MongoDB
    try:
        client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000)
        await client.admin.command('ping')
        db = client[db_name]
        logger.info(f"✅ Connected to MongoDB: {db_name}")
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        sys.exit(1)
    
    logger.info("")
    logger.info("Creating indexes...")
    await create_indexes(db)
    
    logger.info("")
    logger.info("Creating users...")
    
    # Create admin user
    admin_id = await create_user(db, ADMIN_USER)
    
    # Create demo student
    await create_user(db, DEMO_STUDENT)
    
    logger.info("")
    logger.info("Creating courses...")
    
    # Create demo courses
    for course_data in DEMO_COURSES:
        await create_course(db, course_data, admin_id, ADMIN_USER["name"])
    
    # Close connection
    client.close()
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("✅ Database seeding complete!")
    logger.info("=" * 60)
    logger.info("")
    logger.info("📋 Test Credentials:")
    logger.info(f"   Admin:   {ADMIN_USER['email']} / {ADMIN_USER['password']}")
    logger.info(f"   Student: {DEMO_STUDENT['email']} / {DEMO_STUDENT['password']}")
    logger.info("")
    logger.info("💳 Stripe Test Card:")
    logger.info("   Number: 4242 4242 4242 4242")
    logger.info("   Expiry: Any future date (e.g., 12/28)")
    logger.info("   CVC:    Any 3 digits (e.g., 123)")
    logger.info("")

if __name__ == "__main__":
    asyncio.run(seed_database())
