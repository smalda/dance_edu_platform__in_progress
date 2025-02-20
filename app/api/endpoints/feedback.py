"""
1. `GET /feedback/{feedback_id}` - Get specific feedback
2. `POST /feedback/` - Create new feedback
3. `GET /feedback/submission/{submission_id}` - Get all feedback for a submission
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from ...db.base import get_db
from ...schemas.base import Status
from ...schemas.feedback import Feedback
from ...schemas.submission import Submission
from ...schemas.homework import HomeworkTask
from ...schemas.user import User, UserRole
from ...queue.notifications import notify_feedback_provided

router = APIRouter()

@router.get("/{feedback_id}", response_model=Feedback)
def get_feedback_by_id(
    feedback_id: str,
    db: Session = Depends(get_db)
):
    feedback = db.get(Feedback, feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    return feedback

@router.post("/", response_model=Feedback)
def create_feedback(
    feedback: Feedback,
    db: Session = Depends(get_db)
):
    # Verify teacher exists and is actually a teacher
    teacher = db.get(User, feedback.teacher_id)
    if not teacher or teacher.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )

    # Verify submission exists
    submission = db.get(Submission, feedback.submission_id)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )

    # Verify student matches submission
    if feedback.student_id != submission.student_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student ID doesn't match submission's student"
        )

    # Verify teacher matches submission
    if feedback.teacher_id != submission.teacher_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Teacher ID doesn't match submission's teacher"
        )

    try:
        # Add feedback
        db.add(feedback)

        # Update submission status
        submission = db.get(Submission, feedback.submission_id)
        submission.status = Status.COMPLETED

        # Update homework status
        homework = db.get(HomeworkTask, submission.homework_task_id)

        # Check if all students have completed submissions with feedback
        all_completed = True
        for student_id in homework.student_ids:
            student_submission = db.exec(
                select(Submission)
                .where(
                    Submission.homework_task_id == homework.id,
                    Submission.student_id == student_id
                )
            ).first()

            if not student_submission or student_submission.status != Status.COMPLETED:
                all_completed = False
                break

        if all_completed:
            homework.status = Status.COMPLETED

        db.commit()

        # Get notification data for student
        student = db.get(User, feedback.student_id)
        teacher = db.get(User, feedback.teacher_id)

        # Notify student about new feedback
        notify_feedback_provided(
            student_tg_id=student.telegram_id,
            feedback_data={
                "homework_title": homework.content.get("title", "Untitled"),
                "feedback_id": feedback.id,
                "content_preview": feedback.content.get("text", "")[:100] + "..."
                    if len(feedback.content.get("text", "")) > 100
                    else feedback.content.get("text", ""),
                "teacher_name": teacher.tg_handle
            }
        )

        return feedback

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/submission/{submission_id}", response_model=List[Feedback])
def get_submission_feedback(
    submission_id: str,
    submission_status: Optional[str] = None,
    offset: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    # Verify submission exists
    submission = db.get(Submission, submission_id)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )

    query = select(Feedback).where(
        Feedback.submission_id == submission_id
    )

    if submission_status:
        query = query.where(Feedback.status == submission_status)

    feedback_list = db.exec(
        query.offset(offset).limit(limit)
    ).all()

    return feedback_list
