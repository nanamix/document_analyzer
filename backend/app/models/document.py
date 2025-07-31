from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

Base = declarative_base()

class Document(Base):
    """문서 테이블 모델"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # pdf, image
    file_extension = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    extracted_text = Column(Text)
    keywords = Column(JSON)  # 추출된 키워드들
    analysis_result = Column(JSON)  # AI 분석 결과
    user_intent = Column(String)  # 사용자 의도 (예: 면접 준비)
    user_document_type = Column(String)  # 사용자가 지정한 문서 유형 (이력서, 사전과제, 포트폴리오 등)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class DocumentBase(BaseModel):
    """문서 기본 Pydantic 모델"""
    filename: str
    original_filename: str
    file_type: str
    file_extension: str
    user_intent: Optional[str] = None
    user_document_type: Optional[str] = None  # 사용자가 지정한 문서 유형

class DocumentCreate(DocumentBase):
    """문서 생성 모델"""
    file_path: str
    file_size: int

class DocumentResponse(DocumentBase):
    """문서 응답 모델"""
    id: int
    file_size: int
    extracted_text: Optional[str] = None
    keywords: Optional[List[str]] = None
    analysis_result: Optional[Dict[str, Any]] = None
    user_document_type: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class DocumentAnalysis(BaseModel):
    """문서 분석 결과 모델"""
    document_id: int
    keywords: List[str]
    main_topics: List[str]
    document_type: str  # resume, assignment, etc.
    analysis_summary: str
    recommendations: List[str]
    interview_questions: Optional[List[str]] = None
    document_analysis: Optional[Dict[str, Any]] = None  # 각 문서별 세부 분석
    document_relationships: Optional[Dict[str, str]] = None  # 문서 간 연관성
    total_documents: Optional[int] = None  # 총 문서 수
    analysis_method: Optional[str] = None  # 분석 방법

class AnalysisRequest(BaseModel):
    """분석 요청 모델"""
    document_ids: List[int]
    user_intent: str  # "면접 준비", "문서 요약", etc.
    ai_model: Optional[str] = "openai"
    additional_context: Optional[str] = None 