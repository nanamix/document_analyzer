import os
import uuid
import shutil
from pathlib import Path
from typing import List, Optional, Tuple
import aiofiles
import PyPDF2
import pdfplumber
import pytesseract
from PIL import Image
import io
import logging

from config import settings

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """문서 처리 클래스"""
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(exist_ok=True)
        
        # Tesseract 경로 설정
        if settings.TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
    
    async def save_uploaded_file(self, file_content: bytes, filename: str) -> Tuple[str, str]:
        """업로드된 파일을 저장하고 파일 경로 반환"""
        try:
            # 고유한 파일명 생성
            file_extension = Path(filename).suffix.lower()
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = self.upload_dir / unique_filename
            
            # 파일 저장
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
            
            logger.info(f"파일 저장 완료: {file_path}")
            return str(file_path), unique_filename
            
        except Exception as e:
            logger.error(f"파일 저장 중 오류: {e}")
            raise
    
    def validate_file(self, filename: str, file_size: int) -> bool:
        """파일 유효성 검사"""
        # 파일 확장자 검사
        file_extension = Path(filename).suffix.lower().lstrip('.')
        if file_extension not in settings.ALLOWED_EXTENSIONS:
            raise ValueError(f"지원하지 않는 파일 형식입니다. 지원 형식: {settings.ALLOWED_EXTENSIONS}")
        
        # 파일 크기 검사
        if file_size > settings.MAX_FILE_SIZE:
            raise ValueError(f"파일 크기가 너무 큽니다. 최대 크기: {settings.MAX_FILE_SIZE/1024/1024:.1f}MB")
        
        return True
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """PDF에서 텍스트 추출"""
        try:
            text_content = ""
            
            # pdfplumber 사용 (더 정확한 텍스트 추출)
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"
            
            # pdfplumber로 추출이 안 되면 PyPDF2 사용
            if not text_content.strip():
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text_content += page.extract_text() + "\n"
            
            logger.info(f"PDF 텍스트 추출 완료: {len(text_content)} 문자")
            return text_content.strip()
            
        except Exception as e:
            logger.error(f"PDF 텍스트 추출 중 오류: {e}")
            raise
    
    def extract_text_from_image(self, file_path: str) -> str:
        """이미지에서 OCR로 텍스트 추출"""
        try:
            # PIL로 이미지 열기
            image = Image.open(file_path)
            
            # 이미지 전처리 (OCR 정확도 향상)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # OCR 수행 (한국어 + 영어)
            text_content = pytesseract.image_to_string(
                image, 
                lang='kor+eng',
                config='--oem 3 --psm 6'
            )
            
            logger.info(f"이미지 OCR 완료: {len(text_content)} 문자")
            return text_content.strip()
            
        except Exception as e:
            logger.error(f"이미지 OCR 중 오류: {e}")
            # OCR 실패 시 영어만으로 재시도
            try:
                image = Image.open(file_path)
                text_content = pytesseract.image_to_string(image, lang='eng')
                return text_content.strip()
            except:
                raise e
    
    def extract_text(self, file_path: str, file_extension: str) -> str:
        """파일 타입에 따른 텍스트 추출"""
        file_extension = file_extension.lower().lstrip('.')
        
        if file_extension == 'pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_extension in ['png', 'jpg', 'jpeg']:
            return self.extract_text_from_image(file_path)
        else:
            raise ValueError(f"지원하지 않는 파일 형식: {file_extension}")
    
    def cleanup_file(self, file_path: str) -> None:
        """파일 정리"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"파일 삭제 완료: {file_path}")
        except Exception as e:
            logger.error(f"파일 삭제 중 오류: {e}")

# 싱글톤 인스턴스
document_processor = DocumentProcessor() 