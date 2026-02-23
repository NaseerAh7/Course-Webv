from fastapi import APIRouter, HTTPException, Depends
from middleware.auth import require_admin
from typing import List, Callable
from datetime import datetime, timezone

router = APIRouter(prefix="/admin", tags=["Admin"])

# Database dependency
db_dependency: Callable = None

def set_db_dependency(dep: Callable):
    global db_dependency
    db_dependency = dep

def get_db():
    if db_dependency is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    return db_dependency()

@router.get("/users")
async def list_users(admin: dict = Depends(require_admin)):
    db = get_db()
    
    users = await db.users.find({}, {"_id": 0, "password_hash": 0}).to_list(100)
    
    # Parse datetime strings
    for user in users:
        if isinstance(user.get('created_at'), str):
            user['created_at'] = datetime.fromisoformat(user['created_at'])
    
    return users

@router.get("/stats")
async def get_stats(admin: dict = Depends(require_admin)):
    db = get_db()
    
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
    
    return {
        "total_users": total_users,
        "total_courses": total_courses,
        "total_purchases": total_purchases,
        "total_revenue": total_revenue,
        "recent_transactions": recent_transactions
    }

@router.put("/users/{user_id}/role")
async def update_user_role(user_id: str, role: str, admin: dict = Depends(require_admin)):
    db = get_db()
    
    if role not in ["student", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": {"role": role}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": f"User role updated to {role}"}

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, admin: dict = Depends(require_admin)):
    db = get_db()
    
    # Prevent self-deletion
    if user_id == admin['sub']:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    result = await db.users.delete_one({"id": user_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deleted successfully"}
