#!/usr/bin/env python3
"""
Seed script for Course Platform
Creates demo admin user and sample courses
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import uuid
from datetime import datetime, timezone

load_dotenv(Path(__file__).parent / '.env')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Demo courses data
DEMO_COURSES = [
    {
        "id": str(uuid.uuid4()),
        "title": "Complete Web Development Bootcamp 2024",
        "description": "Master web development from scratch! This comprehensive course covers HTML, CSS, JavaScript, React, Node.js, and MongoDB. Perfect for beginners who want to become full-stack developers.",
        "short_description": "Learn full-stack web development from HTML basics to React and Node.js",
        "price": 49.99,
        "thumbnail_url": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=800",
        "category": "Web Development",
        "level": "Beginner",
        "duration_hours": 40,
        "instructor_id": "",  # Will be set to admin ID
        "instructor_name": "Admin User",
        "is_published": True,
        "enrolled_count": 1247,
        "rating": 4.8,
        "lessons": [
            {
                "id": str(uuid.uuid4()),
                "title": "Introduction to Web Development",
                "description": "Learn what web development is and set up your development environment",
                "video_url": "https://www.youtube.com/embed/UB1O30fR-EE",
                "duration_minutes": 15,
                "order": 0
            },
            {
                "id": str(uuid.uuid4()),
                "title": "HTML Fundamentals",
                "description": "Master HTML tags, structure, and semantic markup",
                "video_url": "https://www.youtube.com/embed/qz0aGYrrlhU",
                "duration_minutes": 45,
                "order": 1
            },
            {
                "id": str(uuid.uuid4()),
                "title": "CSS Styling Basics",
                "description": "Learn CSS selectors, properties, and responsive design",
                "video_url": "https://www.youtube.com/embed/1PnVor36_40",
                "duration_minutes": 60,
                "order": 2
            },
            {
                "id": str(uuid.uuid4()),
                "title": "JavaScript Essentials",
                "description": "Understand JavaScript fundamentals and DOM manipulation",
                "video_url": "https://www.youtube.com/embed/W6NZfCO5SIk",
                "duration_minutes": 90,
                "order": 3
            }
        ],
        "pdf_materials": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Python for Data Science & Machine Learning",
        "description": "Dive into the world of data science with Python! Learn NumPy, Pandas, Matplotlib, and scikit-learn to analyze data and build machine learning models.",
        "short_description": "Master Python for data analysis, visualization, and machine learning",
        "price": 79.99,
        "thumbnail_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800",
        "category": "Data Science",
        "level": "Intermediate",
        "duration_hours": 35,
        "instructor_id": "",
        "instructor_name": "Admin User",
        "is_published": True,
        "enrolled_count": 892,
        "rating": 4.9,
        "lessons": [
            {
                "id": str(uuid.uuid4()),
                "title": "Python Basics for Data Science",
                "description": "Review Python fundamentals with a focus on data science applications",
                "video_url": "https://www.youtube.com/embed/rfscVS0vtbw",
                "duration_minutes": 30,
                "order": 0
            },
            {
                "id": str(uuid.uuid4()),
                "title": "NumPy for Numerical Computing",
                "description": "Master arrays, matrices, and numerical operations with NumPy",
                "video_url": "https://www.youtube.com/embed/QUT1VHiLmmI",
                "duration_minutes": 45,
                "order": 1
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Data Analysis with Pandas",
                "description": "Learn DataFrames, data cleaning, and analysis techniques",
                "video_url": "https://www.youtube.com/embed/vmEHCJofslg",
                "duration_minutes": 60,
                "order": 2
            }
        ],
        "pdf_materials": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "title": "UI/UX Design Masterclass",
        "description": "Learn the principles of great design! This course covers user research, wireframing, prototyping, and design systems using Figma.",
        "short_description": "Create stunning user interfaces and seamless user experiences",
        "price": 59.99,
        "thumbnail_url": "https://images.unsplash.com/photo-1561070791-2526d30994b5?w=800",
        "category": "Design",
        "level": "Beginner",
        "duration_hours": 25,
        "instructor_id": "",
        "instructor_name": "Admin User",
        "is_published": True,
        "enrolled_count": 634,
        "rating": 4.7,
        "lessons": [
            {
                "id": str(uuid.uuid4()),
                "title": "Introduction to UI/UX Design",
                "description": "Understand the difference between UI and UX and why both matter",
                "video_url": "https://www.youtube.com/embed/c9Wg6Cb_YlU",
                "duration_minutes": 20,
                "order": 0
            },
            {
                "id": str(uuid.uuid4()),
                "title": "User Research Methods",
                "description": "Learn how to conduct interviews, surveys, and usability tests",
                "video_url": "https://www.youtube.com/embed/TpY1l2bKpAA",
                "duration_minutes": 35,
                "order": 1
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Wireframing and Prototyping",
                "description": "Create low-fidelity and high-fidelity prototypes in Figma",
                "video_url": "https://www.youtube.com/embed/FTFaQWZBqQ8",
                "duration_minutes": 50,
                "order": 2
            }
        ],
        "pdf_materials": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
]

async def seed_database():
    mongo_url = os.environ['MONGO_URL']
    db_name = os.environ['DB_NAME']
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("🌱 Starting database seed...")
    
    # Create admin user
    admin_id = str(uuid.uuid4())
    admin_email = "admin@courseplatform.com"
    admin_password = "admin123"
    
    # Check if admin exists
    existing_admin = await db.users.find_one({"email": admin_email})
    if existing_admin:
        print(f"ℹ️  Admin user already exists: {admin_email}")
        admin_id = existing_admin['id']
    else:
        admin_user = {
            "id": admin_id,
            "email": admin_email,
            "name": "Admin User",
            "password_hash": pwd_context.hash(admin_password),
            "role": "admin",
            "purchased_courses": [],
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(admin_user)
        print(f"✅ Created admin user: {admin_email} / {admin_password}")
    
    # Create demo student
    student_email = "student@demo.com"
    student_password = "student123"
    
    existing_student = await db.users.find_one({"email": student_email})
    if existing_student:
        print(f"ℹ️  Demo student already exists: {student_email}")
    else:
        student_user = {
            "id": str(uuid.uuid4()),
            "email": student_email,
            "name": "Demo Student",
            "password_hash": pwd_context.hash(student_password),
            "role": "student",
            "purchased_courses": [],
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(student_user)
        print(f"✅ Created demo student: {student_email} / {student_password}")
    
    # Create demo courses
    for course in DEMO_COURSES:
        existing_course = await db.courses.find_one({"title": course['title']})
        if existing_course:
            print(f"ℹ️  Course already exists: {course['title']}")
        else:
            course['instructor_id'] = admin_id
            await db.courses.insert_one(course)
            print(f"✅ Created course: {course['title']}")
    
    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index("id", unique=True)
    await db.courses.create_index("id", unique=True)
    await db.payment_transactions.create_index("session_id", unique=True)
    await db.user_progress.create_index([("user_id", 1), ("course_id", 1)])
    
    print("\n✅ Database seeding complete!")
    print("\n📋 Test Credentials:")
    print(f"   Admin: {admin_email} / {admin_password}")
    print(f"   Student: {student_email} / {student_password}")
    print("\n💳 Stripe Test Card: 4242 4242 4242 4242")
    print("   Expiry: Any future date | CVC: Any 3 digits")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())
