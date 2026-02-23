# Digital Course Selling Platform - PRD

## Original Problem Statement
Build a production-ready digital course selling platform with:
- Public pages (Home, Course details, Login, Register)
- Auth system with JWT
- Student Dashboard (purchased courses, video player, PDF download, progress indicator)
- Admin Panel (upload courses, videos, PDFs, set prices, view users)
- Stripe payment integration

## User Personas
1. **Students** - Browse courses, purchase, learn with video player, track progress
2. **Admins** - Create/manage courses, upload content, view users and revenue

## Core Requirements (Static)
- React frontend with Tailwind CSS
- FastAPI backend with MongoDB
- JWT authentication with role-based access
- Stripe payment integration (test mode)
- YouTube embed for videos
- PDF file uploads for course materials
- Progress tracking for students

## What's Been Implemented (Feb 23, 2026)

### Backend
- [x] User authentication (register/login) with JWT
- [x] Role-based authorization (student/admin)
- [x] Course CRUD operations
- [x] Lesson management (YouTube embed URLs)
- [x] PDF upload/download for course materials
- [x] Stripe checkout integration
- [x] Payment status polling
- [x] User progress tracking
- [x] Admin stats and analytics

### Frontend
- [x] Homepage with course catalog, filters, search
- [x] Course details page with purchase button
- [x] Login/Register pages with validation
- [x] Student dashboard with progress tracking
- [x] Course player with YouTube embed
- [x] Admin panel (courses, users, transactions)
- [x] Payment success/cancel pages

### Design
- [x] Professional light theme (Organic & Earthy)
- [x] Fraunces font for headings, DM Sans for body
- [x] Responsive design
- [x] shadcn/ui components

### Data Seeding
- [x] 3 demo courses with lessons
- [x] Admin user: admin@courseplatform.com / admin123
- [x] Student user: student@demo.com / student123

## Prioritized Backlog

### P0 (Critical) - DONE
- User authentication ✅
- Course browsing ✅
- Stripe payments ✅
- Video player ✅
- Progress tracking ✅

### P1 (High Priority)
- Email notifications for purchases
- Course completion certificates
- Coupon/discount codes

### P2 (Medium Priority)
- Course reviews and ratings
- Instructor profiles
- Course categories/tags management
- Search improvements

### P3 (Nice to Have)
- Course bundles
- Affiliate program
- Multi-language support
- Mobile app

## Test Credentials
- **Admin**: admin@courseplatform.com / admin123
- **Student**: student@demo.com / student123
- **Stripe Test Card**: 4242 4242 4242 4242 (any future expiry, any CVC)

## API Endpoints
- POST /api/auth/register - User registration
- POST /api/auth/login - User login
- GET /api/auth/me - Get current user
- GET /api/courses/ - List courses
- GET /api/courses/{id} - Get course details
- POST /api/courses/ - Create course (admin)
- POST /api/payments/checkout/{course_id} - Create Stripe checkout
- GET /api/payments/status/{session_id} - Check payment status
- GET /api/dashboard/my-courses - Get purchased courses
- POST /api/dashboard/course/{id}/progress - Update progress
- GET /api/admin/stats - Admin analytics
- GET /api/admin/users - List users
