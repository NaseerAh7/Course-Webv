import logging
from fastapi import APIRouter, HTTPException, Depends
from middleware.auth import require_admin
from typing import List, Callable
from datetime import datetime, timezone

router = APIRouter(prefix="/admin", tags=["Admin"])
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

@router.get("/users")
async def list_users(admin: dict = Depends(require_admin)):
    """List all users (admin only)."""
    db = get_db()
    
    try:
        users = await db.users.find({}, {"_id": 0, "password_hash": 0}).to_list(100)
        
        # Parse datetime strings
        for user in users:
            if isinstance(user.get('created_at'), str):
                user['created_at'] = datetime.fromisoformat(user['created_at'])
            if isinstance(user.get('updated_at'), str):
                user['updated_at'] = datetime.fromisoformat(user['updated_at'])
        
        logger.info(f"Admin {admin['email']} listed {len(users)} users")
        return users
        
    except Exception as e:
        logger.error(f"Failed to list users: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve users")

@router.get("/stats")
async def get_stats(admin: dict = Depends(require_admin)):
    """Get platform statistics (admin only)."""
    db = get_db()
    
    try:
        total_users = await db.users.count_documents({})
        total_courses = await db.courses.count_documents({})
        total_purchases = await db.payment_transactions.count_documents({"payment_status": "paid"})
        
        # Calculate revenue
        paid_transactions = await db.payment_transactions.find(
            {"payment_status": "paid"},
            {"_id": 0, "amount": 1}
        ).to_list(1000)
        
        total_revenue = sum(t.get('amount', 0) for t in paid_transactions)
        
        # Recent transactions
        recent_transactions = await db.payment_transactions.find(
            {},
            {"_id": 0}
        ).sort("created_at", -1).limit(10).to_list(10)
        
        logger.info(f"Admin {admin['email']} viewed stats")
        
        return {
            "total_users": total_users,
            "total_courses": total_courses,
            "total_purchases": total_purchases,
            "total_revenue": total_revenue,
            "recent_transactions": recent_transactions
        }
        
    except Exception as e:
        logger.error(f"Failed to get stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")

@router.put("/users/{user_id}/role")
async def update_user_role(user_id: str, role: str, admin: dict = Depends(require_admin)):
    """Update a user's role (admin only)."""
    db = get_db()
    
    try:
        if role not in ["student", "admin"]:
            raise HTTPException(status_code=400, detail="Invalid role. Must be 'student' or 'admin'")
        
        result = await db.users.update_one(
            {"id": user_id},
            {"$set": {
                "role": role,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"Admin {admin['email']} updated user {user_id} role to {role}")
        return {"message": f"User role updated to {role}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user role: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update user role")

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, admin: dict = Depends(require_admin)):
    """Delete a user (admin only)."""
    db = get_db()
    
    try:
        # Prevent self-deletion
        if user_id == admin['sub']:
            raise HTTPException(status_code=400, detail="Cannot delete yourself")
        
        result = await db.users.delete_one({"id": user_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"Admin {admin['email']} deleted user {user_id}")
        return {"message": "User deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete user")
