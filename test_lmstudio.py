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
                analysis_prompt = """다음 텍스트를 분석하여 JSON 형식으로 응답해주세요:

텍스트: "저는 컴퓨터 과학을 전공한 개발자입니다. Python과 JavaScript에 능숙하며, 웹 개발 경험이 3년 있습니다."

다음 형식으로 응답해주세요:
{
    "document_type": "문서 유형",
    "keywords": ["키워드1", "키워드2"],
    "summary": "요약",
    "recommendations": ["추천사항1"]
}"""
                
                analysis_response = await client.post(
                    f"{settings.LMSTUDIO_BASE_URL}/v1/chat/completions",
                    json={
                        "model": settings.LMSTUDIO_MODEL,
                        "messages": [
                            {"role": "user", "content": analysis_prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 500,
                        "stream": False
                    },
                    timeout=30.0
                )
                
                if analysis_response.status_code == 200:
                    analysis_result = analysis_response.json()
                    analysis_text = analysis_result["choices"][0]["message"]["content"]
                    print("✅ 문서 분석 형식 테스트 성공!")
                    print(f"분석 응답: {analysis_text[:200]}...")
                    
                    # JSON 파싱 테스트
                    try:
                        json.loads(analysis_text)
                        print("✅ JSON 파싱 성공!")
                    except json.JSONDecodeError:
                        print("⚠️  JSON 파싱 실패 - 모델이 정확한 JSON을 생성하지 못함")
                        print("💡 모델에게 JSON 형식을 더 명확히 요청하거나 다른 모델을 사용해보세요.")
                
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