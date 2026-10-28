from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.security import get_optional_current_user
from app.models.user import User
from app.models.analysis import Analysis
from app.services.report_generator import generate_analysis_pdf_report

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/{analysis_id}")
def download_pdf_report(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_current_user),
):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis record not found for PDF generation.",
        )

    # If the analysis is associated with a user, ensure only the owner can download it
    if analysis.user_id is not None:
        if not current_user or current_user.id != analysis.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view or download this audit report.",
            )

    pdf_buffer = generate_analysis_pdf_report(analysis)
    filename = f"codewithanil-audit-report-{analysis.id}.pdf"

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
