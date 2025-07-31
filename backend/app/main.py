from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import os

from config import settings
from app.database import create_tables
from app.api.documents import router as documents_router

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# multipart 경고 숨기기
logging.getLogger("python_multipart.multipart").setLevel(logging.ERROR)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # 시작 시 실행
    logger.info("Document Analyzer API 시작")
    
    # 업로드 디렉토리 생성
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # 데이터베이스 테이블 생성
    create_tables()
    
    yield
    
    # 종료 시 실행
    logger.info("Document Analyzer API 종료")

# FastAPI 앱 생성
app = FastAPI(
    title="Document Analyzer API",
    description="AI를 활용한 문서 분석 시스템",
    version="1.0.0",
    lifespan=lifespan,
    # multipart 경고 해결을 위한 설정
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(documents_router)

# 정적 파일 서빙 (업로드된 파일들)
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

@app.get("/")
async def root():
    """API 루트 엔드포인트"""
    return {
        "message": "Document Analyzer API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "api_keys_configured": {
            "openai": bool(settings.OPENAI_API_KEY),
            "anthropic": bool(settings.ANTHROPIC_API_KEY),
            "deepseek": bool(settings.DEEPSEEK_API_KEY),
            "grok": bool(settings.GROK_API_KEY)
        }
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """글로벌 예외 처리기"""
    logger.error(f"전역 오류 발생: {exc}")
    return HTTPException(status_code=500, detail="내부 서버 오류가 발생했습니다")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        # multipart 경고 해결을 위한 추가 설정
        access_log=True
    ) 