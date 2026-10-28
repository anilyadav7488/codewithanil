from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.analysis import Analysis
from app.schemas.analysis import AnalysisHistoryItem, TextAnalysisResponse, UserStatsResponse

router = APIRouter(prefix="/analysis", tags=["History & User Data"])

@router.get("/history", response_model=List[AnalysisHistoryItem])
def get_analysis_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    records = (
        db.query(Analysis)
        .filter(Analysis.user_id == current_user.id)
        .order_by(Analysis.created_at.desc())
        .limit(100)
        .all()
    )

    items = []
    for r in records:
        items.append(
            AnalysisHistoryItem(
                id=r.id,
                user_id=r.user_id,
                analysis_type=r.analysis_type,
                prediction=r.prediction,
                model_score=r.model_score,
                model_version=r.model_version,
                word_count=r.word_count,
                snippet=r.text_snippet,
                created_at=r.created_at,
                has_report=True,
            )
        )
    return items

@router.get("/stats", response_model=UserStatsResponse)
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user_id = current_user.id
    total = db.query(Analysis).filter(Analysis.user_id == user_id).count()
    ai_count = db.query(Analysis).filter(Analysis.user_id == user_id, Analysis.prediction == "AI-Generated").count()
    human_count = db.query(Analysis).filter(Analysis.user_id == user_id, Analysis.prediction == "Human").count()
    inconclusive_count = db.query(Analysis).filter(Analysis.user_id == user_id, Analysis.prediction == "Inconclusive").count()

    avg_score = db.query(func.avg(Analysis.model_score)).filter(Analysis.user_id == user_id).scalar() or 0.0
    total_words = db.query(func.sum(Analysis.word_count)).filter(Analysis.user_id == user_id).scalar() or 0

    return UserStatsResponse(
        total_analyses=total,
        ai_count=ai_count,
        human_count=human_count,
        inconclusive_count=inconclusive_count,
        average_ai_score=round(float(avg_score), 3),
        total_words_analyzed=int(total_words),
    )

@router.get("/{analysis_id}", response_model=TextAnalysisResponse)
def get_analysis_by_id(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id, Analysis.user_id == current_user.id).first()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis record not found.")

    return TextAnalysisResponse(
        id=analysis.id,
        input_text=analysis.input_text or analysis.text_snippet,
        word_count=analysis.word_count,
        character_count=analysis.character_count,
        prediction=analysis.prediction,
        ai_score=analysis.model_score,
        human_score=analysis.human_score,
        is_inconclusive=analysis.is_inconclusive,
        confidence_level="High" if abs(analysis.model_score - 0.5) > 0.3 else "Medium",
        model_name=analysis.model_name,
        model_version=analysis.model_version,
        processing_time_ms=analysis.processing_time_ms,
        limitations=[
            "Probabilistic estimate based on syntactic and perplexity patterns.",
            "Historical record retrieved from secure database.",
        ],
        created_at=analysis.created_at,
    )

@router.delete("/{analysis_id}")
def delete_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id, Analysis.user_id == current_user.id).first()
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found.")

    db.delete(analysis)
    db.commit()
    return {"success": True, "message": "Record successfully removed from database."}
