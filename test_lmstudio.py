#!/usr/bin/env python3
"""
LM Studio 연결 테스트 스크립트
"""
import asyncio
import httpx
import json
import sys
import os

# 백엔드 경로를 sys.path에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.config import settings

async def test_lmstudio_connection():
    """LM Studio 연결 테스트"""
    print("🖥️  LM Studio 연결 테스트 시작...")
    print(f"URL: {settings.LMSTUDIO_BASE_URL}")
    print(f"모델: {settings.LMSTUDIO_MODEL}")
    
    try:
        async with httpx.AsyncClient() as client:
            # 1. 서버 상태 확인
            print("\n1️⃣ 서버 상태 확인 중...")
            try:
                response = await client.get(f"{settings.LMSTUDIO_BASE_URL}/v1/models", timeout=5.0)
                if response.status_code == 200:
                    models = response.json()
                    print("✅ LM Studio 서버 연결 성공!")
                    print(f"사용 가능한 모델: {len(models.get('data', []))}개")
                    for model in models.get('data', []):
                        print(f"  - {model.get('id', 'Unknown')}")
                else:
                    print(f"⚠️  서버 응답 오류: {response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ 서버 연결 실패: {e}")
                print("💡 LM Studio가 실행 중인지 확인하세요!")
                return False
            
            # 2. 간단한 채팅 테스트
            print("\n2️⃣ 채팅 API 테스트 중...")
            test_prompt = "안녕하세요! 간단한 인사말로 응답해주세요."
            
            chat_response = await client.post(
                f"{settings.LMSTUDIO_BASE_URL}/v1/chat/completions",
                json={
                    "model": settings.LMSTUDIO_MODEL,
                    "messages": [
                        {"role": "user", "content": test_prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 100,
                    "stream": False
                },
                timeout=30.0
            )
            
            if chat_response.status_code == 200:
                result = chat_response.json()
                ai_response = result["choices"][0]["message"]["content"]
                print("✅ 채팅 API 테스트 성공!")
                print(f"AI 응답: {ai_response[:100]}...")
                
                # 3. 문서 분석 형식 테스트
                print("\n3️⃣ 문서 분석 형식 테스트 중...")
                system_prompt = """당신은 문서 분석 전문가입니다. 
반드시 올바른 JSON 형식으로만 응답해야 합니다. 
추가 설명이나 마크다운 형식 없이 순수한 JSON만 출력하세요.

IMPORTANT: 응답에는 JSON 이외의 다른 텍스트를 포함하지 마세요."""

                user_prompt = """다음 문서를 분석하고 JSON 형식으로만 응답하세요:

문서 내용: "저는 컴퓨터 과학을 전공한 개발자입니다. Python과 JavaScript에 능숙하며, 웹 개발 경험이 3년 있습니다."
사용자 의도: 면접 준비

다음 형식의 JSON만 출력하세요:
{
    "document_type": "문서 유형",
    "keywords": ["키워드1", "키워드2"],
    "main_topics": ["주제1", "주제2"],
    "summary": "요약",
    "recommendations": ["추천사항1"],
    "interview_questions": ["질문1", "질문2"]
}"""
                
                analysis_response = await client.post(
                    f"{settings.LMSTUDIO_BASE_URL}/v1/chat/completions",
                    json={
                        "model": settings.LMSTUDIO_MODEL,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.1,
                        "max_tokens": 800,
                        "stream": False
                    },
                    timeout=30.0
                )
                
                if analysis_response.status_code == 200:
                    analysis_result = analysis_response.json()
                    analysis_text = analysis_result["choices"][0]["message"]["content"]
                    print("✅ 문서 분석 형식 테스트 성공!")
                    print(f"분석 응답: {analysis_text[:200]}...")
                    
                    # JSON 파싱 테스트 (개선된 추출 로직 사용)
                    try:
                        # 1. 마크다운 코드 블록에서 JSON 추출 시도
                        import re
                        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', analysis_text, re.DOTALL)
                        if json_match:
                            json_str = json_match.group(1)
                            result = json.loads(json_str)
                            print("✅ JSON 파싱 성공! (마크다운 코드 블록에서 추출)")
                        else:
                            # 2. 중괄호로 둘러싸인 JSON 찾기
                            brace_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
                            if brace_match:
                                json_str = brace_match.group(0)
                                result = json.loads(json_str)
                                print("✅ JSON 파싱 성공! (중괄호 패턴으로 추출)")
                            else:
                                # 3. 직접 JSON 파싱 시도
                                result = json.loads(analysis_text)
                                print("✅ JSON 파싱 성공! (직접 파싱)")
                        
                        print(f"📊 추출된 키워드: {result.get('keywords', [])}")
                        print(f"📄 문서 유형: {result.get('document_type', 'Unknown')}")
                        
                    except json.JSONDecodeError:
                        print("⚠️  JSON 파싱 실패 - 모든 추출 방법 실패")
                        print("💡 모델 설정을 확인하거나 다른 모델을 사용해보세요.")
                        print(f"🔍 원본 응답 미리보기: {analysis_text[:300]}...")
                        return False
                
                return True
            else:
                print(f"❌ 채팅 API 오류: {chat_response.status_code}")
                print(f"응답: {chat_response.text}")
                return False
                
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        return False

async def main():
    """메인 함수"""
    print("=" * 50)
    print("🖥️  LM Studio 연결 테스트")
    print("=" * 50)
    
    # 설정 확인
    print(f"설정된 LM Studio URL: {settings.LMSTUDIO_BASE_URL}")
    print(f"설정된 모델명: {settings.LMSTUDIO_MODEL}")
    
    success = await test_lmstudio_connection()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 LM Studio 연결 테스트 완료!")
        print("✅ Document Analyzer에서 LM Studio를 사용할 수 있습니다.")
    else:
        print("❌ LM Studio 연결 테스트 실패")
        print("🔧 문제 해결 방법:")
        print("  1. LM Studio 앱이 실행 중인지 확인")
        print("  2. 로컬 서버가 활성화되어 있는지 확인")
        print("  3. 포트 1234가 사용 중인지 확인")
        print("  4. 모델이 로드되어 있는지 확인")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main()) 