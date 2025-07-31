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
                    result = self._extract_and_parse_json(result_text)
                except json.JSONDecodeError:
                    logger.warning(f"Ollama JSON 파싱 실패. 원본 응답: {result_text[:200]}...")
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
    
    async def analyze_with_lmstudio(self, text: str, user_intent: str, additional_context: str = "") -> Dict[str, Any]:
        """LM Studio 로컬 AI를 이용한 분석 (OpenAI 호환 API)"""
        try:
            if not settings.LMSTUDIO_BASE_URL:
                raise ValueError("LM Studio 설정이 없습니다")
            
            system_prompt = """당신은 문서 분석 전문가입니다. 
반드시 올바른 JSON 형식으로만 응답해야 합니다. 
추가 설명이나 마크다운 형식 없이 순수한 JSON만 출력하세요.

응답 형식:
{
    "document_type": "문서 유형",
    "keywords": ["키워드1", "키워드2", "키워드3"],
    "main_topics": ["주제1", "주제2"],
    "summary": "문서 요약",
    "recommendations": ["추천1", "추천2"],
    "interview_questions": ["질문1", "질문2"]
}

IMPORTANT: 응답에는 JSON 이외의 다른 텍스트를 포함하지 마세요."""

            user_prompt = f"""다음 문서를 분석하고 JSON 형식으로만 응답하세요:

문서 내용: {text}
사용자 의도: {user_intent}
추가 컨텍스트: {additional_context}

분석 요구사항:
1. document_type: 문서 유형 분류
2. keywords: 주요 키워드 5-10개 추출
3. main_topics: 주요 주제 3-5개
4. summary: 문서 요약 (2-3문장)
5. recommendations: 추천사항 2-3개
6. interview_questions: 면접 질문 3-5개 (면접 준비 의도인 경우)

JSON만 출력하세요:"""

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.LMSTUDIO_BASE_URL}/v1/chat/completions",
                    json={
                        "model": settings.LMSTUDIO_MODEL,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.1,
                        "max_tokens": 1500,
                        "stream": False
                    },
                    timeout=60.0
                )
            
            if response.status_code == 200:
                result_data = response.json()
                result_text = result_data["choices"][0]["message"]["content"]
                
                try:
                    # JSON 추출 및 파싱 시도
                    result = self._extract_and_parse_json(result_text)
                    result["analysis_method"] = "LM Studio 로컬 분석"
                except json.JSONDecodeError:
                    # JSON 파싱 실패 시 로컬 분석으로 fallback
                    logger.warning(f"LM Studio JSON 파싱 실패. 원본 응답: {result_text[:200]}...")
                    result = self.generate_local_analysis(text, user_intent)
                    result["analysis_method"] = "로컬 분석 (LM Studio JSON 파싱 실패)"
                
                return {
                    "ai_model": "lmstudio",
                    "analysis": result,
                    "raw_response": result_text
                }
            else:
                raise Exception(f"LM Studio API 오류: {response.status_code}")
                
        except Exception as e:
            logger.error(f"LM Studio 분석 중 오류: {e}")
            # LM Studio 실패 시 로컬 분석으로 fallback
            local_result = self.generate_local_analysis(text, user_intent)
            local_result["analysis_method"] = "로컬 분석 (LM Studio 실패)"
            return {
                "ai_model": "local_fallback",
                "analysis": local_result,
                "raw_response": f"LM Studio 오류로 로컬 분석 사용: {str(e)}"
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
    
    def _extract_and_parse_json(self, text: str) -> Dict[str, Any]:
        """텍스트에서 JSON 추출 및 파싱 (마크다운 코드 블록 등 처리)"""
        # 1. 마크다운 코드 블록에서 JSON 추출 시도
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        # 2. 중괄호로 둘러싸인 JSON 찾기
        brace_match = re.search(r'\{.*\}', text, re.DOTALL)
        if brace_match:
            json_str = brace_match.group(0)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        # 3. 직접 JSON 파싱 시도
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # 4. 모든 시도 실패 시 예외 발생
        raise json.JSONDecodeError("JSON 추출 실패", text, 0)

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
    
    def _classify_document_types(self, texts: List[str], user_document_types: List[str] = None) -> List[str]:
        """여러 문서의 유형을 각각 분류 (사용자 지정 우선)"""
        doc_types = []
        
        for i, text in enumerate(texts):
            # 사용자가 지정한 문서 유형이 있으면 우선 사용
            if user_document_types and i < len(user_document_types) and user_document_types[i]:
                doc_types.append(user_document_types[i])
            else:
                # 자동 분류 사용
                doc_type = self.classify_document_type(text)
                doc_types.append(doc_type)
        
        return doc_types

    def _generate_comprehensive_analysis(self, texts: List[str], doc_types: List[str], user_intent: str) -> Dict[str, Any]:
        """면접 준비를 위한 종합 분석"""
        try:
            # 전체 텍스트 통합
            combined_text = "\n\n".join(texts)
            
            # 각 문서별 키워드 추출
            all_keywords = []
            for text in texts:
                keywords = self.extract_keywords(text, 8)
                all_keywords.extend(keywords)
            
            # 중복 제거 및 빈도순 정렬
            from collections import Counter
            keyword_counts = Counter(all_keywords)
            top_keywords = [word for word, count in keyword_counts.most_common(15)]
            
            # 문서 유형별 분석
            doc_analysis = {}
            for i, (text, doc_type) in enumerate(zip(texts, doc_types)):
                doc_analysis[f"문서{i+1}"] = {
                    "type": doc_type,
                    "keywords": self.extract_keywords(text, 5),
                    "summary": text[:200] + "..." if len(text) > 200 else text
                }
            
            # 면접 준비 특화 분석
            if user_intent == "면접 준비":
                recommendations = self._generate_interview_recommendations(doc_types, top_keywords)
                interview_questions = self._generate_comprehensive_interview_questions(doc_types, top_keywords, texts)
            else:
                recommendations = [
                    "문서들의 주요 키워드를 파악했습니다",
                    "문서 간 연관성을 검토해보세요",
                    "핵심 내용을 요약하여 정리하세요"
                ]
                interview_questions = []
            
            # 문서 간 연관성 분석
            relationships = self._analyze_document_relationships(doc_types)
            
            return {
                "document_type": f"다중문서 ({', '.join(set(doc_types))})",
                "keywords": top_keywords,
                "main_topics": list(set([kw for kw in top_keywords[:5]])),
                "summary": self._generate_multi_document_summary(texts, doc_types),
                "recommendations": recommendations,
                "interview_questions": interview_questions,
                "document_analysis": doc_analysis,
                "document_relationships": relationships,
                "total_documents": len(texts),
                "analysis_method": "종합 다중 문서 분석"
            }
            
        except Exception as e:
            logger.error(f"종합 분석 중 오류: {e}")
            # 기본 분석으로 fallback
            combined_text = "\n\n=== 문서 구분 ===\n\n".join(texts)
            return self.generate_local_analysis(combined_text, user_intent)

    def _generate_interview_recommendations(self, doc_types: List[str], keywords: List[str]) -> List[str]:
        """면접 준비 추천사항 생성"""
        recommendations = []
        
        # 문서 유형별 추천사항
        if "이력서" in doc_types:
            recommendations.append("이력서의 모든 경험에 대해 구체적인 사례와 성과를 준비하세요")
            recommendations.append("경력 중 가장 도전적이었던 프로젝트와 극복 과정을 설명할 수 있도록 준비하세요")
        
        if "사전과제" in doc_types:
            recommendations.append("사전과제의 핵심 기술과 설계 결정에 대한 근거를 명확히 설명할 수 있어야 합니다")
            recommendations.append("과제에서 사용한 기술 스택의 장단점과 대안에 대해 생각해보세요")
        
        if "포트폴리오" in doc_types:
            recommendations.append("포트폴리오의 각 프로젝트별 기술적 도전과 해결책을 정리하세요")
            recommendations.append("프로젝트의 비즈니스 임팩트와 개선사항을 구체적으로 준비하세요")
        
        # 키워드 기반 추천사항
        tech_keywords = [kw for kw in keywords if any(tech in kw.lower() for tech in 
                        ['python', 'javascript', 'react', 'node', 'sql', 'aws', 'docker', 'git'])]
        
        if tech_keywords:
            recommendations.append(f"주요 기술 스택({', '.join(tech_keywords[:3])})에 대한 심화 질문을 준비하세요")
        
        # 기본 추천사항
        recommendations.extend([
            "자기소개를 1분, 3분, 5분 버전으로 각각 준비하세요",
            "지원 동기와 회사에 대한 이해도를 명확히 표현할 수 있어야 합니다",
            "향후 커리어 계획과 성장 목표를 구체적으로 준비하세요"
        ])
        
        return recommendations[:8]  # 최대 8개

    def _generate_comprehensive_interview_questions(self, doc_types: List[str], keywords: List[str], texts: List[str]) -> List[str]:
        """종합적인 면접 예상 질문 생성"""
        questions = []
        
        # 자기소개 관련
        questions.append("간단하게 자기소개를 해주세요")
        questions.append("지원 동기와 우리 회사를 선택한 이유를 말씀해주세요")
        
        # 문서별 특화 질문
        if "이력서" in doc_types:
            if keywords:
                questions.append(f"{keywords[0]}에 대한 경험을 구체적으로 설명해주세요")
            questions.append("가장 자랑스러운 프로젝트나 성과는 무엇인가요?")
            questions.append("팀에서 갈등이 있었던 경험과 해결 방법을 말씀해주세요")
        
        if "사전과제" in doc_types:
            questions.append("사전과제에서 가장 어려웠던 부분과 해결 과정을 설명해주세요")
            questions.append("과제에서 사용한 기술을 선택한 이유는 무엇인가요?")
            questions.append("과제를 다시 한다면 어떤 부분을 개선하고 싶나요?")
        
        if "포트폴리오" in doc_types:
            questions.append("포트폴리오에서 가장 기술적으로 도전적이었던 프로젝트는 무엇인가요?")
            questions.append("프로젝트의 성과를 어떻게 측정했나요?")
        
        # 기술 관련 질문
        tech_keywords = [kw for kw in keywords[:5] if len(kw) > 2]
        for tech in tech_keywords[:2]:
            questions.append(f"{tech}의 장단점과 사용 경험을 설명해주세요")
        
        # 일반적인 질문
        questions.extend([
            "개발자로서 가장 중요하게 생각하는 가치는 무엇인가요?",
            "새로운 기술을 학습하는 본인만의 방법이 있나요?",
            "5년 후 본인의 모습을 어떻게 그리고 있나요?",
            "우리 팀에서 어떤 기여를 할 수 있을까요?",
            "마지막으로 궁금한 점이나 하고 싶은 말씀이 있나요?"
        ])
        
        return questions[:15]  # 최대 15개

    def _analyze_document_relationships(self, doc_types: List[str]) -> Dict[str, str]:
        """문서 간 연관성 분석"""
        relationships = {}
        
        unique_types = list(set(doc_types))
        
        if len(unique_types) > 1:
            if "이력서" in unique_types and "사전과제" in unique_types:
                relationships["이력서-사전과제"] = "이력서의 경험이 사전과제 해결에 어떻게 활용되었는지 연결지어 설명할 수 있어야 합니다"
            
            if "이력서" in unique_types and "포트폴리오" in unique_types:
                relationships["이력서-포트폴리오"] = "이력서의 경력과 포트폴리오 프로젝트의 연관성을 강조하여 일관된 스토리를 만드세요"
            
            if "사전과제" in unique_types and "포트폴리오" in unique_types:
                relationships["사전과제-포트폴리오"] = "포트폴리오의 경험이 사전과제 접근 방식에 어떤 영향을 주었는지 설명하세요"
        
        return relationships

    def _generate_multi_document_summary(self, texts: List[str], doc_types: List[str]) -> str:
        """다중 문서 종합 요약"""
        summary_parts = []
        
        # 문서 개수와 유형
        summary_parts.append(f"총 {len(texts)}개의 문서가 분석되었습니다.")
        
        # 문서 유형별 요약
        type_counts = {}
        for doc_type in doc_types:
            type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
        
        type_summary = ", ".join([f"{dtype} {count}개" for dtype, count in type_counts.items()])
        summary_parts.append(f"문서 구성: {type_summary}")
        
        # 종합 평가
        if "이력서" in doc_types and "사전과제" in doc_types:
            summary_parts.append("이력서와 사전과제가 함께 제출되어 지원자의 역량을 종합적으로 평가할 수 있습니다.")
        
        return " ".join(summary_parts)

    def _create_structured_prompt(self, texts: List[str], doc_types: List[str], user_intent: str, additional_context: str) -> str:
        """AI 모델용 구조화된 프롬프트 생성"""
        prompt_parts = []
        
        # 헤더
        prompt_parts.append("=== 다중 문서 종합 분석 요청 ===")
        prompt_parts.append(f"분석 목적: {user_intent}")
        prompt_parts.append(f"문서 개수: {len(texts)}개")
        prompt_parts.append(f"문서 유형: {', '.join(doc_types)}")
        
        if additional_context:
            prompt_parts.append(f"추가 컨텍스트: {additional_context}")
        
        prompt_parts.append("")
        
        # 각 문서별 구분
        for i, (text, doc_type) in enumerate(zip(texts, doc_types)):
            prompt_parts.append(f"=== 문서 {i+1}: {doc_type} ===")
            prompt_parts.append(text)
            prompt_parts.append("")
        
        # 분석 요청사항
        prompt_parts.append("=== 분석 요청사항 ===")
        if user_intent == "면접 준비":
            prompt_parts.append("면접 준비를 위한 종합 분석을 수행해주세요:")
            prompt_parts.append("1. 각 문서별 핵심 내용 파악")
            prompt_parts.append("2. 문서들 간의 연관성 분석")
            prompt_parts.append("3. 통합된 키워드 추출")
            prompt_parts.append("4. 면접 예상 질문 생성 (문서별 + 종합)")
            prompt_parts.append("5. 면접 준비 전략 제시")
        else:
            prompt_parts.append("다중 문서 종합 분석을 수행해주세요:")
            prompt_parts.append("1. 각 문서의 주요 내용")
            prompt_parts.append("2. 공통 키워드 및 주제")
            prompt_parts.append("3. 문서들의 전체적인 관점")
        
        return "\n".join(prompt_parts)

    async def analyze_documents(self, 
                              texts: List[str], 
                              user_intent: str, 
                              ai_model: str = "local",
                              additional_context: str = "",
                              user_consent: bool = False,
                              user_document_types: List[str] = None) -> Dict[str, Any]:
        """여러 문서 통합 분석 (보안 우선) - 면접 준비 특화"""
        try:
            # 문서 유형 분류 (사용자 지정 우선)
            doc_types = self._classify_document_types(texts, user_document_types)
            
            # 텍스트 결합 (항상 정의)
            combined_text = "\n\n=== 문서 구분 ===\n\n".join(texts)
            
            # 면접 준비나 다중 문서인 경우 종합 분석 수행
            if user_intent == "면접 준비" or len(texts) > 1:
                logger.info(f"🎯 종합 분석 시작: {len(texts)}개 문서, 유형: {doc_types}")
                
                # 🔒 로컬 분석인 경우 종합 분석 사용
                if ai_model == "local" or ai_model == "basic":
                    analysis_result = self._generate_comprehensive_analysis(texts, doc_types, user_intent)
                    result = {
                        "ai_model": "local",
                        "analysis": analysis_result,
                        "raw_response": "종합 로컬 분석 수행"
                    }
                    # 추가 분석 정보
                    result["analysis"]["total_documents"] = len(texts)
                    result["analysis"]["total_characters"] = len(combined_text)
                    result["analysis"]["security_level"] = "높음"
                    return result
                else:
                    # AI 모델 사용 시 종합 분석 프롬프트 적용
                    combined_text = self._create_structured_prompt(texts, doc_types, user_intent, additional_context)
            
            # 🔒 AI 모델별 분석 수행
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
                
            elif ai_model == "lmstudio":
                # LM Studio 로컬 AI 분석
                result = await self.analyze_with_lmstudio(combined_text, user_intent, additional_context)
                
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
            result["analysis"]["security_level"] = "높음" if ai_model in ["local", "ollama", "lmstudio"] else "주의"
            
            return result
            
        except Exception as e:
            logger.error(f"문서 분석 중 오류: {e}")
            # 모든 실패 시 로컬 분석 (안전한 fallback)
            try:
                fallback_text = "\n\n=== 문서 구분 ===\n\n".join(texts)
                analysis_result = self.generate_local_analysis(fallback_text, user_intent)
                return {
                    "ai_model": "local_emergency",
                    "analysis": analysis_result,
                    "raw_response": f"오류로 인한 로컬 분석: {str(e)}"
                }
            except Exception as fallback_error:
                logger.error(f"Fallback 분석도 실패: {fallback_error}")
                return {
                    "ai_model": "error",
                    "analysis": {
                        "document_type": "분석 실패",
                        "keywords": [],
                        "main_topics": [],
                        "summary": f"분석 중 오류가 발생했습니다: {str(e)}",
                        "recommendations": ["나중에 다시 시도해주세요"],
                        "interview_questions": []
                    },
                    "raw_response": f"완전 실패: {str(e)}"
                }

# 싱글톤 인스턴스
ai_analyzer = AIAnalyzer() 