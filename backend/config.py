import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") 
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    GROK_API_KEY = os.getenv("GROK_API_KEY")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./document_analyzer.db")
    
    # 배포 환경 설정
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")  # development, production
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    
    # File Upload
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "50000000"))  # 50MB
    ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "pdf"]
    
    # 🔒 보안 설정 - 데이터 보호 우선
    ENABLE_EXTERNAL_AI = os.getenv("ENABLE_EXTERNAL_AI", "false").lower() == "true"
    REQUIRE_EXPLICIT_CONSENT = os.getenv("REQUIRE_EXPLICIT_CONSENT", "true").lower() == "true"
    DEFAULT_AI_MODEL = os.getenv("DEFAULT_AI_MODEL", "local")  # 로컬 분석 기본값
    ENABLE_DATA_MASKING = os.getenv("ENABLE_DATA_MASKING", "true").lower() == "true"
    
    # AI Model Settings
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-sonnet-20240229")
    
    # 로컬 AI 설정
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
    
    # LM Studio 설정 (OpenAI 호환 API)
    LMSTUDIO_BASE_URL = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234")
    LMSTUDIO_MODEL = os.getenv("LMSTUDIO_MODEL", "local-model")
    
    # OCR Settings - macOS 기본값 (Homebrew 설치 기준)
    TESSERACT_CMD = os.getenv("TESSERACT_CMD", "/opt/homebrew/bin/tesseract")
    
    # 민감 정보 패턴 (마스킹용)
    SENSITIVE_PATTERNS = [
        r'\b\d{3}-\d{2}-\d{4}\b',  # SSN 패턴
        r'\b\d{3}-\d{4}-\d{4}\b',  # 전화번호
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # 이메일
        r'\b\d{4}-\d{4}-\d{4}-\d{4}\b',  # 카드번호 패턴
    ]
    
    # CORS - 포트 4001로 변경 (충돌 방지)
    ALLOWED_ORIGINS = [
        "http://localhost:4001",
        "http://localhost:8080",
        "http://127.0.0.1:4001",
        "http://127.0.0.1:8080",
    ]

settings = Settings() 