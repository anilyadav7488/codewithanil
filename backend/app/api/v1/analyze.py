import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Response
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.security import get_optional_current_user
from app.models.user import User
from app.models.analysis import Analysis
from app.models.document import Document
from app.schemas.analysis import TextAnalysisRequest, TextAnalysisResponse
from app.schemas.prompt import PromptAnalysisRequest, PromptAnalysisResponse
from app.schemas.document import DocumentAnalysisResponse
from app.services.prompt_evaluator import evaluate_prompt
from app.services.document_parser import validate_uploaded_file, extract_text_from_file_bytes
from ml.inference import AIModelInferenceService, ModelNotReadyError, ModelInitializingError

logger = logging.getLogger("codewithanil.api.analyze")

router = APIRouter(prefix="/analyze", tags=["Analysis"])

@router.post("/text", response_model=TextAnalysisResponse)
def analyze_text(
    payload: TextAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    service = AIModelInferenceService.get_instance()
    try:
        result = service.predict_text(
            raw_text=payload.text,
            include_sentences=payload.include_sentences,
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except ModelInitializingError as mie:
        logger.warning(f"[Inference 503] Model initializing: {mie}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Inference service is currently initializing. Please try again in a few seconds.",
            headers={"Retry-After": "5"}
        )
    except ModelNotReadyError as mnre:
        logger.error(f"[Inference 503] Model not ready: {mnre}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Inference service unavailable: {str(mnre)}",
            headers={"Retry-After": "10"}
        )
    except Exception as e:
        logger.error(f"[Inference 500] Unexpected inference failure: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error: {str(e)}",
        )

    # If user wants to save to database history and is authenticated
    db_id = None
    if payload.save_history and current_user:
        # Save analysis record
        db_analysis = Analysis(
            user_id=current_user.id,
            input_text=payload.text if payload.save_history else None,
            text_snippet=result["input_text"][:250],
            analysis_type="text",
            word_count=result["word_count"],
            character_count=result["character_count"],
            prediction=result["prediction"],
            model_score=result["ai_score"],
            human_score=result["human_score"],
            is_inconclusive=result["is_inconclusive"],
            model_name=result["model_name"],
            model_version=result["model_version"],
            processing_time_ms=result["processing_time_ms"],
        )
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        db_id = db_analysis.id

    result["id"] = db_id
    return result

@router.post("/prompt", response_model=PromptAnalysisResponse)
def analyze_prompt(payload: PromptAnalysisRequest):
    try:
        return evaluate_prompt(payload.prompt)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prompt audit error: {str(e)}",
        )

@router.post("/document", response_model=DocumentAnalysisResponse)
async def analyze_document(
    file: UploadFile = File(...),
    save_history: bool = Form(default=True),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    ext = validate_uploaded_file(file)
    content = await file.read()

    # Reject files larger than max limit
    max_bytes = 15 * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds maximum 15MB limit.",
        )

    # Extract text safely
    extracted_text, requires_ocr = extract_text_from_file_bytes(content, ext)

    # Run ML Model
    service = AIModelInferenceService.get_instance()
    try:
        ml_result = service.predict_text(
            raw_text=extracted_text,
            include_sentences=True,
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except ModelInitializingError as mie:
        logger.warning(f"[Document Inference 503] Model initializing: {mie}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Inference service is currently initializing. Please try again in a few seconds.",
            headers={"Retry-After": "5"}
        )
    except ModelNotReadyError as mnre:
        logger.error(f"[Document Inference 503] Model not ready: {mnre}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Inference service unavailable: {str(mnre)}",
            headers={"Retry-After": "10"}
        )
    except Exception as e:
        logger.error(f"[Document Inference Error] {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document inference failure: {str(e)}",
        )

    # Persist in DB if user is authenticated or document audit is active
    user_id = current_user.id if current_user else None
    db_analysis = Analysis(
        user_id=user_id,
        input_text=extracted_text if save_history else None,
        text_snippet=extracted_text[:250],
        analysis_type="document",
        word_count=ml_result["word_count"],
        character_count=ml_result["character_count"],
        prediction=ml_result["prediction"],
        model_score=ml_result["ai_score"],
        human_score=ml_result["human_score"],
        is_inconclusive=ml_result["is_inconclusive"],
        model_name=ml_result["model_name"],
        model_version=ml_result["model_version"],
        processing_time_ms=ml_result["processing_time_ms"],
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)

    db_doc = Document(
        user_id=user_id,
        analysis_id=db_analysis.id,
        filename=file.filename or f"document{ext}",
        file_type=ext.replace(".", ""),
        file_size_bytes=len(content),
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)

    ml_result["id"] = db_analysis.id

    return DocumentAnalysisResponse(
        document_id=db_doc.id,
        filename=db_doc.filename,
        file_type=db_doc.file_type,
        extracted_word_count=ml_result["word_count"],
        text_preview=extracted_text[:500] + ("..." if len(extracted_text) > 500 else ""),
        requires_ocr_warning=requires_ocr,
        analysis=TextAnalysisResponse(**ml_result),
    )
