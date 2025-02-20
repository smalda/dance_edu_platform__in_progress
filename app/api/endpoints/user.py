"""
1. `/users/me` - Get current user by telegram handle
2. `/users/{user_id}` - Get user by ID
3. `/users/by_handle/{tg_handle}` - Get user by telegram handle
4. `/users/` - Get all users (with optional role filter)
5. `/users/students/` - Get all students
6. `/users/teachers/` - Get all teachers
7. `/users/` (POST) - Create new user
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, or_
from typing import List, Optional
from ...db.base import get_db
from ...schemas.user import User, UserRole

router = APIRouter()

# @router.get("/me", response_model=User)
# def get_current_user(
#     tg_handle: str,  # This would come from auth/security in real app
#     db: Session = Depends(get_db)
# ):
#     user = db.exec(
#         select(User).where(User.tg_handle == tg_handle)
#     ).first()

#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found"
#         )
#     return user

@router.get("/by_telegram_id/{telegram_id}", response_model=User)
def get_user_by_telegram_id(
    telegram_id: str,
    db: Session = Depends(get_db)
):
    user = db.exec(
        select(User).where(User.telegram_id == telegram_id)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.get("/by_telegram_handle/{tg_handle}", response_model=User)
def get_user_by_telegram_handle(
    tg_handle: str,  # This would come from auth/security in real app
    db: Session = Depends(get_db)
):
    user = db.exec(
        select(User).where(User.tg_handle == tg_handle)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.get("/{user_id}", response_model=User)
def get_user_by_id(
    user_id: str,
    db: Session = Depends(get_db)
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

# @router.get("/by_handle/{tg_handle}", response_model=User)
# def get_user_by_handle(
#     tg_handle: str,
#     db: Session = Depends(get_db)
# ):
#     user = db.exec(
#         select(User).where(User.tg_handle == tg_handle)
#     ).first()

#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found"
#         )
#     return user

@router.get("/", response_model=List[User])
async def get_users(
    role: Optional[UserRole] = None,
    offset: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = select(User)
    if role:
        query = query.where(User.role == role)

    users = db.exec(
        query.offset(offset).limit(limit)
    ).all()
    return users

@router.get("/students/", response_model=List[User])
def get_all_students(
    offset: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    students = db.exec(
        select(User)
        .where(User.role == UserRole.STUDENT)
        .offset(offset)
        .limit(limit)
    ).all()
    return students

@router.get("/teachers/", response_model=List[User])
def get_all_teachers(
    offset: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    teachers = db.exec(
        select(User)
        .where(User.role == UserRole.TEACHER)
        .offset(offset)
        .limit(limit)
    ).all()
    return teachers

@router.post("/", response_model=User)
async def create_user(
    user: User,
    db: Session = Depends(get_db)
):
    if user.role not in [UserRole.STUDENT, UserRole.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid user role"
        )

    if user.tg_handle == "":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot have an empty telegram handle for user"
        )

    # Check if user with this handle already exists
    existing_user = db.exec(
        select(User).where(
            or_(
                User.tg_handle == user.tg_handle,
                User.telegram_id == user.telegram_id
            )
        )
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this telegram handle or ID already exists"
        )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user
