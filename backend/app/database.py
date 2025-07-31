from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import logging

from config import settings

logger = logging.getLogger(__name__)

# 데이터베이스 엔진 생성
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# 세션 팩토리
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스
Base = declarative_base()

def create_tables():
    """테이블 생성"""
    try:
        from app.models.document import Base as DocumentBase
        DocumentBase.metadata.create_all(bind=engine)
        logger.info("데이터베이스 테이블 생성 완료")
    except Exception as e:
        logger.error(f"테이블 생성 중 오류: {e}")
        raise

@contextmanager
def get_db_session():
    """데이터베이스 세션 컨텍스트 매니저"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"데이터베이스 오류: {e}")
        raise
    finally:
        session.close()

def get_db():
    """FastAPI 의존성용 데이터베이스 세션"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 