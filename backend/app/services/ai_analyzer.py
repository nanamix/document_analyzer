import openai
import anthropic
import httpx
import json
import logging
import re
from typing import List, Dict, Any, Optional
from langdetect import detect
from collections import Counter

from config import settings

logger = logging.getLogger(__name__)

class AIAnalyzer:
    """AI 모델을 이용한 문서 분석 클래스 (보안 강화)"""
    
    def __init__(self):
        # 🔒 보안 우선: 외부 AI 사용 시에만 클라이언트 초기화
        self.external_ai_enabled = settings.ENABLE_EXTERNAL_AI
        
        if self.external_ai_enabled:
            # OpenAI 클라이언트 초기화
            if settings.OPENAI_API_KEY:
                self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Anthropic Claude 클라이언트 초기화
            if settings.ANTHROPIC_API_KEY:
                self.anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        else:
            logger.info("🔒 외부 AI 비활성화 - 로컬 분석만 사용")
    
    def mask_sensitive_data(self, text: str) -> str:
        """민감한 정보 마스킹"""
        if not settings.ENABLE_DATA_MASKING:
            return text
            
        masked_text = text
        for pattern in settings.SENSITIVE_PATTERNS:
            masked_text = re.sub(pattern, '[MASKED]', masked_text)
        
        return masked_text
    
    def extract_keywords(self, text: str, num_keywords: int = 10) -> List[str]:
        """텍스트에서 키워드 추출 (로컬 처리)"""
        try:
            # 한국어/영어 감지
            try:
                lang = detect(text)
            except:
                lang = 'ko'
            
            # 기본적인 키워드 추출 (빈도 기반)
            # 특수문자 제거 및 단어 분리
            words = re.findall(r'\b[가-힣a-zA-Z]{2,}\b', text)
            
            # 불용어 제거 (확장된 버전)
            stopwords = {
                # 한국어 불용어
                '그리고', '하지만', '그런데', '그래서', '따라서', '또한', '그러나', '이것', '그것', '저것',
                '있다', '없다', '이다', '아니다', '하다', '되다', '같다', '다른', '많은', '작은', '큰',
                '좋은', '나쁜', '새로운', '오래된', '첫번째', '두번째', '마지막', '처음', '나중',
                # 영어 불용어
                'and', 'but', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
                'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did',
                'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must', 'shall',
                'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
            }
            
            filtered_words = [word.lower() for word in words if word.lower() not in stopwords and len(word) > 2]
            
            # 빈도 계산
            word_freq = Counter(filtered_words)
            
            # 상위 키워드 반환
            keywords = [word for word, freq in word_freq.most_common(num_keywords)]
            
            return keywords
            
        except Exception as e:
            logger.error(f"키워드 추출 중 오류: {e}")
            return []
    
    def classify_document_type(self, text: str) -> str:
        """문서 유형 분류 (로컬 처리)"""
        text_lower = text.lower()
        
        # 키워드 기반 문서 분류
        if any(keyword in text_lower for keyword in ['이력서', 'resume', 'cv', '경력', 'experience', '학력', 'education']):
            return '이력서'
        elif any(keyword in text_lower for keyword in ['자기소개서', 'cover letter', '지원동기', '포부']):
            return '자기소개서'
        elif any(keyword in text_lower for keyword in ['과제', 'assignment', 'project', '프로젝트']):
            return '사전과제'
        elif any(keyword in text_lower for keyword in ['포트폴리오', 'portfolio', '작품집']):
            return '포트폴리오'
        elif any(keyword in text_lower for keyword in ['논문', 'paper', 'thesis', '연구']):
            return '논문/연구자료'
        elif any(keyword in text_lower for keyword in ['계약서', 'contract', '약관']):
            return '계약서'
        elif any(keyword in text_lower for keyword in ['보고서', 'report', '분석']):
            return '보고서'
        else:
            return '일반 문서'
    
    def generate_local_analysis(self, text: str, user_intent: str) -> Dict[str, Any]:
        """로컬 분석 (외부 AI 없이)"""
        try:
            keywords = self.extract_keywords(text, 15)
            doc_type = self.classify_document_type(text)
            
            # 기본 요약 (첫 200자)
            summary = text[:200] + "..." if len(text) > 200 else text
            
            # 사용자 의도에 따른 추천사항
            recommendations = []
            interview_questions = []
            
            if user_intent == "면접 준비":
                recommendations = [
                    "추출된 키워드를 중심으로 답변을 준비하세요",
                    "구체적인 경험과 성과를 수치로 준비하세요",
                    "해당 분야의 최신 트렌드를 학습하세요"
                ]
                
                # 키워드 기반 기본 면접 질문 생성
                if keywords:
                    interview_questions = [
                        f"{keywords[0]}에 대한 경험을 설명해 주세요",
                        f"{keywords[1] if len(keywords) > 1 else '해당 분야'}에서 가장 어려웠던 점은 무엇인가요?",
                        "앞으로의 목표와 계획에 대해 말씀해 주세요"
                    ]
            
            elif user_intent == "문서 요약":
                recommendations = [
                    "핵심 키워드를 중심으로 내용을 정리했습니다",
                    "중요한 세부사항은 원문을 다시 확인하세요"
                ]
            
            elif user_intent == "키워드 추출":
                recommendations = [
                    "추출된 키워드를 SEO나 태그로 활용할 수 있습니다",
                    "관련 키워드를 추가로 연구해 보세요"
                ]
            
            return {
                "document_type": doc_type,
                "keywords": keywords,
                "main_topics": keywords[:5],
                "summary": summary,
                "recommendations": recommendations,
                "interview_questions": interview_questions,
                "analysis_method": "로컬 분석 (보안 우선)"
            }
            
        except Exception as e:
            logger.error(f"로컬 분석 중 오류: {e}")
            return {
                "document_type": "문서",
                "keywords": [],
                "main_topics": [],
                "summary": "분석 중 오류가 발생했습니다",
                "recommendations": ["문서를 다시 확인해 주세요"],
                "interview_questions": [],
                "analysis_method": "로컬 분석 (오류)"
            }
    
    async def analyze_with_external_ai(self, text: str, user_intent: str, ai_model: str, 
                                     additional_context: str = "", user_consent: bool = False) -> Dict[str, Any]:
        """외부 AI를 이용한 분석 (사용자 동의 필요)"""
        
        # 🔒 보안 체크
        if not self.external_ai_enabled:
            raise ValueError("외부 AI 사용이 비활성화되어 있습니다")
        
        if settings.REQUIRE_EXPLICIT_CONSENT and not user_consent:
            raise ValueError("외부 AI 사용을 위해 명시적 동의가 필요합니다")
        
        # 민감한 정보 마스킹
        masked_text = self.mask_sensitive_data(text)
        
        logger.warning(f"🔒 외부 AI 사용 중: {ai_model} - 데이터가 외부 서버로 전송됩니다")
        
        try:
            if ai_model == "openai" and settings.OPENAI_API_KEY:
                return await self.analyze_with_openai(masked_text, user_intent, additional_context)
            elif ai_model == "claude" and settings.ANTHROPIC_API_KEY:
                return await self.analyze_with_claude(masked_text, user_intent, additional_context)
            elif ai_model == "deepseek" and settings.DEEPSEEK_API_KEY:
                return await self.analyze_with_deepseek(masked_text, user_intent, additional_context)
            else:
                raise ValueError(f"지원하지 않는 AI 모델이거나 API 키가 없습니다: {ai_model}")
                
        except Exception as e:
            logger.error(f"외부 AI 분석 중 오류: {e}")
            # 외부 AI 실패 시 로컬 분석으로 fallback
            logger.info("외부 AI 실패 - 로컬 분석으로 전환")
            local_result = self.generate_local_analysis(text, user_intent)
            local_result["analysis_method"] = f"로컬 분석 (외부 AI {ai_model} 실패)"
            return {
                "ai_model": "local_fallback",
                "analysis": local_result,
                "raw_response": f"외부 AI 오류로 로컬 분석 사용: {str(e)}"
            }
    
    async def analyze_with_ollama(self, text: str, user_intent: str, additional_context: str = "") -> Dict[str, Any]:
        """Ollama 로컬 AI를 이용한 분석"""
        try:
            if not settings.OLLAMA_BASE_URL:
                raise ValueError("Ollama 설정이 없습니다")
            
            prompt = f"""다음 문서를 분석해주세요:

문서 내용:
{text}

사용자 의도: {user_intent}
추가 컨텍스트: {additional_context}

다음 항목들을 JSON 형식으로 분석해주세요:
1. document_type: 문서 유형
2. keywords: 주요 키워드 10개 (배열)
3. main_topics: 주요 주제들 (배열)
4. summary: 문서 요약
5. recommendations: 추천사항 (배열)
6. interview_questions: 면접 예상 질문 (배열, 면접 준비 의도인 경우)

JSON 형식으로만 응답해주세요."""

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.OLLAMA_BASE_URL}/api/generate",
                    json={
                        "model": settings.OLLAMA_MODEL,
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=30.0
                )
            
            if response.status_code == 200:
                result_data = response.json()
                result_text = result_data.get("response", "")
                
                try:
                    result = json.loads(result_text)
                except json.JSONDecodeError:
                    result = self.generate_local_analysis(text, user_intent)
                    result["analysis_method"] = "로컬 분석 (Ollama JSON 파싱 실패)"
                
                return {
                    "ai_model": "ollama",
                    "analysis": result,
                    "raw_response": result_text
                }
            else:
                raise Exception(f"Ollama API 오류: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Ollama 분석 중 오류: {e}")
            # Ollama 실패 시 로컬 분석으로 fallback
            local_result = self.generate_local_analysis(text, user_intent)
            local_result["analysis_method"] = "로컬 분석 (Ollama 실패)"
            return {
                "ai_model": "local_fallback",
                "analysis": local_result,
                "raw_response": f"Ollama 오류로 로컬 분석 사용: {str(e)}"
            }
    
    async def analyze_with_openai(self, text: str, user_intent: str, additional_context: str = "") -> Dict[str, Any]:
        """OpenAI를 이용한 문서 분석 (마스킹된 데이터)"""
        try:
            system_prompt = """당신은 문서 분석 전문가입니다. 주어진 문서를 분석하여 다음 정보를 제공해주세요:
1. 문서 유형 (이력서, 사전과제, 포트폴리오 등)
2. 주요 키워드 10개
3. 주요 주제들
4. 문서 요약
5. 추천사항
6. 면접 시 예상 질문 (사용자 의도가 면접 준비인 경우)

응답은 반드시 JSON 형식으로 해주세요."""
            
            user_prompt = f"""
분석할 문서 내용:
{text}

사용자 의도: {user_intent}
추가 컨텍스트: {additional_context}

위 문서를 분석하여 JSON 형식으로 결과를 제공해주세요.
"""
            
            response = await self.openai_client.chat.completions.acreate(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content
            
            # JSON 파싱 시도
            try:
                result = json.loads(result_text)
                result["analysis_method"] = "OpenAI 분석 (마스킹된 데이터)"
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 기본 구조로 파싱
                result = self._parse_text_response(result_text)
                result["analysis_method"] = "OpenAI 분석 (JSON 파싱 실패)"
            
            return {
                "ai_model": "openai",
                "analysis": result,
                "raw_response": result_text
            }
            
        except Exception as e:
            logger.error(f"OpenAI 분석 중 오류: {e}")
            raise
    
    async def analyze_with_claude(self, text: str, user_intent: str, additional_context: str = "") -> Dict[str, Any]:
        """Claude를 이용한 문서 분석 (마스킹된 데이터)"""
        try:
            prompt = f"""다음 문서를 분석해주세요:

문서 내용:
{text}

사용자 의도: {user_intent}
추가 컨텍스트: {additional_context}

다음 항목들을 JSON 형식으로 분석해주세요:
1. document_type: 문서 유형
2. keywords: 주요 키워드 10개 (배열)
3. main_topics: 주요 주제들 (배열)
4. summary: 문서 요약
5. recommendations: 추천사항 (배열)
6. interview_questions: 면접 예상 질문 (배열, 면접 준비 의도인 경우)

JSON 형식으로만 응답해주세요."""
            
            message = await self.anthropic_client.messages.acreate(
                model=settings.CLAUDE_MODEL,
                max_tokens=2000,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            result_text = message.content[0].text
            
            # JSON 파싱 시도
            try:
                result = json.loads(result_text)
                result["analysis_method"] = "Claude 분석 (마스킹된 데이터)"
            except json.JSONDecodeError:
                result = self._parse_text_response(result_text)
                result["analysis_method"] = "Claude 분석 (JSON 파싱 실패)"
            
            return {
                "ai_model": "claude",
                "analysis": result,
                "raw_response": result_text
            }
            
        except Exception as e:
            logger.error(f"Claude 분석 중 오류: {e}")
            raise
    
    async def analyze_with_deepseek(self, text: str, user_intent: str, additional_context: str = "") -> Dict[str, Any]:
        """DeepSeek API를 이용한 문서 분석 (마스킹된 데이터)"""
        try:
            if not settings.DEEPSEEK_API_KEY:
                raise ValueError("DeepSeek API 키가 설정되지 않았습니다.")
            
            # DeepSeek API 호출 (OpenAI 호환 API 사용)
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {
                                "role": "system",
                                "content": "당신은 문서 분석 전문가입니다. JSON 형식으로 분석 결과를 제공해주세요."
                            },
                            {
                                "role": "user", 
                                "content": f"문서: {text}\n사용자 의도: {user_intent}\n분석 요청"
                            }
                        ],
                        "temperature": 0.7,
                        "max_tokens": 2000
                    }
                )
            
            if response.status_code == 200:
                result_data = response.json()
                result_text = result_data["choices"][0]["message"]["content"]
                
                try:
                    result = json.loads(result_text)
                    result["analysis_method"] = "DeepSeek 분석 (마스킹된 데이터)"
                except json.JSONDecodeError:
                    result = self._parse_text_response(result_text)
                    result["analysis_method"] = "DeepSeek 분석 (JSON 파싱 실패)"
                
                return {
                    "ai_model": "deepseek",
                    "analysis": result,
                    "raw_response": result_text
                }
            else:
                raise Exception(f"DeepSeek API 오류: {response.status_code}")
                
        except Exception as e:
            logger.error(f"DeepSeek 분석 중 오류: {e}")
            raise
    
    def _parse_text_response(self, text: str) -> Dict[str, Any]:
        """텍스트 응답을 기본 JSON 구조로 파싱"""
        return {
            "document_type": "문서",
            "keywords": self.extract_keywords(text, 10),
            "main_topics": ["분석 결과"],
            "summary": text[:500] + "..." if len(text) > 500 else text,
            "recommendations": ["AI 분석을 통한 추가 검토 권장"],
            "interview_questions": [],
            "analysis_method": "텍스트 파싱"
        }
    
    async def analyze_documents(self, 
                              texts: List[str], 
                              user_intent: str, 
                              ai_model: str = "local",
                              additional_context: str = "",
                              user_consent: bool = False) -> Dict[str, Any]:
        """여러 문서 통합 분석 (보안 우선)"""
        try:
            # 모든 텍스트 합치기
            combined_text = "\n\n=== 문서 구분 ===\n\n".join(texts)
            
            # 🔒 보안 우선 분석 순서
            if ai_model == "local" or ai_model == "basic":
                # 로컬 분석 (가장 안전)
                analysis_result = self.generate_local_analysis(combined_text, user_intent)
                result = {
                    "ai_model": "local",
                    "analysis": analysis_result,
                    "raw_response": "로컬 분석 수행"
                }
                
            elif ai_model == "ollama":
                # Ollama 로컬 AI 분석
                result = await self.analyze_with_ollama(combined_text, user_intent, additional_context)
                
            elif ai_model in ["openai", "claude", "deepseek"]:
                # 외부 AI 분석 (사용자 동의 필요)
                result = await self.analyze_with_external_ai(
                    combined_text, user_intent, ai_model, additional_context, user_consent
                )
                
            else:
                # 알 수 없는 모델 - 로컬 분석으로 fallback
                logger.warning(f"알 수 없는 AI 모델: {ai_model} - 로컬 분석 사용")
                analysis_result = self.generate_local_analysis(combined_text, user_intent)
                result = {
                    "ai_model": "local_fallback",
                    "analysis": analysis_result,
                    "raw_response": f"알 수 없는 모델 {ai_model} - 로컬 분석 사용"
                }
            
            # 추가 분석 정보
            result["analysis"]["total_documents"] = len(texts)
            result["analysis"]["total_characters"] = len(combined_text)
            result["analysis"]["security_level"] = "높음" if ai_model in ["local", "ollama"] else "주의"
            
            return result
            
        except Exception as e:
            logger.error(f"문서 분석 중 오류: {e}")
            # 모든 실패 시 로컬 분석
            analysis_result = self.generate_local_analysis(combined_text, user_intent)
            return {
                "ai_model": "local_emergency",
                "analysis": analysis_result,
                "raw_response": f"오류로 인한 로컬 분석: {str(e)}"
            }

# 싱글톤 인스턴스
ai_analyzer = AIAnalyzer() 