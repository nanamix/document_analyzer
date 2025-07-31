from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import json

from app.database import get_db
from app.models.document import Document, DocumentResponse, DocumentCreate, AnalysisRequest, DocumentAnalysis
from app.services.document_processor import document_processor
from app.services.ai_analyzer import ai_analyzer
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.post("/upload", response_model=List[DocumentResponse])
async def upload_documents(
    files: List[UploadFile] = File(..., description="업로드할 파일들"),
    user_intent: Optional[str] = Form(None, description="사용자 의도"),
    db: Session = Depends(get_db)
):
    """문서 업로드 API"""
    try:
        uploaded_documents = []
        
        for file in files:
            # 파일 내용 읽기
            file_content = await file.read()
            file_size = len(file_content)
            
            # 파일 유효성 검사
            document_processor.validate_file(file.filename, file_size)
            
            # 파일 저장
            file_path, unique_filename = await document_processor.save_uploaded_file(
                file_content, file.filename
            )
            
            # 텍스트 추출
            file_extension = file.filename.split('.')[-1].lower()
            try:
                extracted_text = document_processor.extract_text(file_path, file_extension)
                logger.info(f"✅ 텍스트 추출 완료: {len(extracted_text)} 문자")
            except Exception as e:
                logger.warning(f"텍스트 추출 실패: {e}")
                extracted_text = ""
            
            # 문서 정보 DB 저장
            db_document = Document(
                filename=unique_filename,
                original_filename=file.filename,
                file_path=file_path,
                file_type="pdf" if file_extension == "pdf" else "image",
                file_extension=file_extension,
                file_size=file_size,
                extracted_text=extracted_text,
                user_intent=user_intent
            )
            
            db.add(db_document)
            db.commit()
            db.refresh(db_document)
            
            uploaded_documents.append(db_document)
            
            logger.info(f"📄 문서 업로드 완료: {file.filename} -> {unique_filename}")
        
        return uploaded_documents
        
    except Exception as e:
        logger.error(f"문서 업로드 중 오류: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[DocumentResponse])
def get_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """문서 목록 조회 API"""
    try:
        documents = db.query(Document).offset(skip).limit(limit).all()
        return documents
    except Exception as e:
        logger.error(f"문서 목록 조회 중 오류: {e}")
        raise HTTPException(status_code=500, detail="문서 목록 조회 실패")

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db)):
    """특정 문서 조회 API"""
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다")
        return document
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"문서 조회 중 오류: {e}")
        raise HTTPException(status_code=500, detail="문서 조회 실패")

# 🔒 보안 강화된 분석 요청 모델
class SecureAnalysisRequest(AnalysisRequest):
    user_consent: bool = False  # 외부 AI 사용 동의

@router.post("/analyze", response_model=DocumentAnalysis)
async def analyze_documents(
    request: SecureAnalysisRequest,
    db: Session = Depends(get_db)
):
    """🔒 보안 강화된 문서 분석 API"""
    try:
        # 🔒 보안 체크 1: 외부 AI 사용 가능 여부
        external_ai_models = ["openai", "claude", "deepseek"]
        is_external_ai = request.ai_model in external_ai_models
        
        if is_external_ai and not settings.ENABLE_EXTERNAL_AI:
            logger.warning(f"🔒 외부 AI 사용 시도 차단: {request.ai_model}")
            raise HTTPException(
                status_code=403, 
                detail="외부 AI 사용이 비활성화되어 있습니다. 로컬 분석을 사용해주세요."
            )
        
        # 🔒 보안 체크 2: 사용자 동의 확인
        if is_external_ai and settings.REQUIRE_EXPLICIT_CONSENT and not request.user_consent:
            logger.warning(f"🔒 사용자 동의 없는 외부 AI 사용 시도: {request.ai_model}")
            raise HTTPException(
                status_code=403, 
                detail="외부 AI 사용을 위해 명시적 동의가 필요합니다."
            )
        
        # 문서들 조회
        documents = db.query(Document).filter(Document.id.in_(request.document_ids)).all()
        
        if not documents:
            raise HTTPException(status_code=404, detail="분석할 문서를 찾을 수 없습니다")
        
        # 텍스트 추출
        texts = []
        for doc in documents:
            if doc.extracted_text:
                texts.append(doc.extracted_text)
            else:
                # 텍스트가 없으면 다시 추출 시도
                try:
                    extracted_text = document_processor.extract_text(doc.file_path, doc.file_extension)
                    doc.extracted_text = extracted_text
                    texts.append(extracted_text)
                except Exception as e:
                    logger.warning(f"문서 {doc.id} 텍스트 추출 실패: {e}")
                    continue
        
        if not texts:
            raise HTTPException(status_code=400, detail="분석할 텍스트가 없습니다")
        
        # 🔒 보안 로깅
        security_level = "높음" if request.ai_model in ["local", "ollama"] else "주의"
        logger.info(f"🔒 문서 분석 시작 - 모델: {request.ai_model}, 보안 수준: {security_level}")
        
        if is_external_ai:
            logger.warning(f"⚠️ 외부 AI 사용: {request.ai_model} - 사용자 동의: {request.user_consent}")
        
        # AI 분석 수행
        analysis_result = await ai_analyzer.analyze_documents(
            texts=texts,
            user_intent=request.user_intent,
            ai_model=request.ai_model or "local",  # 기본값: 로컬
            additional_context=request.additional_context or "",
            user_consent=request.user_consent
        )
        
        # 분석 결과를 첫 번째 문서에 저장 (대표 문서)
        main_document = documents[0]
        main_document.analysis_result = analysis_result
        main_document.user_intent = request.user_intent
        
        # 키워드 추출 및 저장
        analysis_data = analysis_result.get("analysis", {})
        keywords = analysis_data.get("keywords", [])
        main_document.keywords = keywords
        
        db.commit()
        
        # 응답 데이터 구성
        response_data = DocumentAnalysis(
            document_id=main_document.id,
            keywords=keywords,
            main_topics=analysis_data.get("main_topics", []),
            document_type=analysis_data.get("document_type", "문서"),
            analysis_summary=analysis_data.get("summary", ""),
            recommendations=analysis_data.get("recommendations", []),
            interview_questions=analysis_data.get("interview_questions", []),
            document_analysis=analysis_data.get("document_analysis", {}),
            document_relationships=analysis_data.get("document_relationships", {}),
            total_documents=analysis_data.get("total_documents", len(documents)),
            analysis_method=analysis_data.get("analysis_method", "기본 분석")
        )
        
        logger.info(f"✅ 문서 분석 완료: {len(documents)}개 문서, 보안 수준: {security_level}")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"문서 분석 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"문서 분석 실패: {str(e)}")

@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """문서 삭제 API"""
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다")
        
        # 파일 삭제
        document_processor.cleanup_file(document.file_path)
        
        # DB에서 삭제
        db.delete(document)
        db.commit()
        
        logger.info(f"🗑️ 문서 삭제 완료: {document.original_filename}")
        return {"message": "문서 삭제 완료"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"문서 삭제 중 오류: {e}")
        raise HTTPException(status_code=500, detail="문서 삭제 실패")

@router.get("/{document_id}/analysis")
def get_document_analysis(document_id: int, db: Session = Depends(get_db)):
    """문서 분석 결과 조회 API"""
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다")
        
        if not document.analysis_result:
            raise HTTPException(status_code=404, detail="분석 결과가 없습니다")
        
        return document.analysis_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"분석 결과 조회 중 오류: {e}")
        raise HTTPException(status_code=500, detail="분석 결과 조회 실패")

@router.get("/security/status")
async def get_security_status():
    """🔒 보안 상태 확인 API"""
    return {
        "external_ai_enabled": settings.ENABLE_EXTERNAL_AI,
        "require_explicit_consent": settings.REQUIRE_EXPLICIT_CONSENT,
        "data_masking_enabled": settings.ENABLE_DATA_MASKING,
        "default_ai_model": settings.DEFAULT_AI_MODEL,
        "available_models": {
            "local": "로컬 분석 (가장 안전)",
            "ollama": "Ollama 로컬 AI" if settings.OLLAMA_BASE_URL else "설치 필요",
            "openai": "사용 가능" if settings.OPENAI_API_KEY and settings.ENABLE_EXTERNAL_AI else "비활성화",
            "claude": "사용 가능" if settings.ANTHROPIC_API_KEY and settings.ENABLE_EXTERNAL_AI else "비활성화",
            "deepseek": "사용 가능" if settings.DEEPSEEK_API_KEY and settings.ENABLE_EXTERNAL_AI else "비활성화"
        },
        "security_recommendations": [
            "로컬 분석 또는 Ollama 사용 권장",
            "기업 기밀 문서는 외부 AI 사용 금지",
            "외부 AI 사용 시 사용자 동의 필요",
            "민감한 정보 자동 마스킹 활성화"
        ]
    } 