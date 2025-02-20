"""
1. `GET /homework/{homework_id}` - Get specific homework
2. `POST /homework/assign/` - Assign new homework
3. `GET /homework/student/{student_id}` - Get all homework for a student
4. `GET /homework/teacher/{teacher_id}` - Get all homework from a teacher
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from ...db.base import get_db
from ...schemas.base import Status
from ...schemas.homework import HomeworkTask
from ...schemas.user import User, UserRole
from ...queue.notifications import notify_homework_assigned

router = APIRouter()

@router.get("/{homework_id}", response_model=HomeworkTask)
def get_homework_by_id(
    homework_id: str,
    db: Session = Depends(get_db)
):
    homework = db.get(HomeworkTask, homework_id)
    if not homework:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Homework not found"
        )
    return homework

@router.post("/assign/", response_model=HomeworkTask)
def assign_homework(
    homework: HomeworkTask,
    db: Session = Depends(get_db)
):
    # Verify teacher exists and is actually a teacher
    teacher = db.get(User, homework.teacher_id)
    if not teacher or teacher.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )

    # Verify all students exist
    students = db.exec(
        select(User).where(
            User.id.in_(homework.student_ids),
            User.role == UserRole.STUDENT
        )
    ).all()

    if len(students) != len(homework.student_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more student IDs are invalid"
        )

    db.add(homework)
    db.commit()
    db.refresh(homework)

    # Notify each student about new homework
    for student in students:
        notify_homework_assigned(
            student_tg_id=student.telegram_id,
            homework_data={
                "title": homework.content.get("title"),
                "description": homework.content.get("description")
            }
        )

    return homework

@router.get("/student/{student_id}", response_model=List[HomeworkTask])
def get_student_homework(
    student_id: str,
    homework_status: Optional[str] = None,
    offset: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    # Verify student exists and is actually a student
    student = db.get(User, student_id)
    if not student or student.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )

    query = select(HomeworkTask).where(
        HomeworkTask.student_ids.contains([student_id])
    )

    if homework_status:
        query = query.where(HomeworkTask.status == homework_status)

    homework = db.exec(
        query.offset(offset).limit(limit)
    ).all()

    return homework

@router.get("/teacher/{teacher_id}", response_model=List[HomeworkTask])
def get_teacher_homework(
    teacher_id: str,
    homework_status: Optional[str] = None,
    offset: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    # Verify teacher exists and is actually a teacher
    teacher = db.get(User, teacher_id)
    if not teacher or teacher.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )

    query = select(HomeworkTask).where(
        HomeworkTask.teacher_id == teacher_id
    )

    if homework_status:
        query = query.where(HomeworkTask.status == homework_status)

    homework = db.exec(
        query.offset(offset).limit(limit)
    ).all()

    return homework

@router.patch("/{homework_id}/status")
def update_homework_status(
    homework_id: str,
    status: Status,
    db: Session = Depends(get_db)
):
    homework = db.get(HomeworkTask, homework_id)
    if not homework:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Homework not found"
        )

    homework.status = status
    db.commit()
    db.refresh(homework)
    return homework
