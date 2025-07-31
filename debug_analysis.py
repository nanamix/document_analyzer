#!/usr/bin/env python3
"""
분석 결과 디버깅 스크립트
"""
import sys
import os
import asyncio
import httpx

# 백엔드 경로를 sys.path에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_analysis_flow():
    """분석 플로우 테스트"""
    base_url = "http://localhost:4000"
    
    async with httpx.AsyncClient() as client:
        print("🔍 문서 분석 플로우 디버깅")
        print("=" * 50)
        
        # 1. 서버 상태 확인
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                print("✅ 백엔드 서버 연결 성공")
            else:
                print("❌ 백엔드 서버 연결 실패")
                return
        except Exception as e:
            print(f"❌ 서버 연결 오류: {e}")
            return
        
        # 2. 문서 목록 조회
        try:
            response = await client.get(f"{base_url}/api/documents/")
            if response.status_code == 200:
                documents = response.json()
                print(f"📄 문서 목록: {len(documents)}개 문서 발견")
                
                for doc in documents:
                    print(f"  - ID {doc['id']}: {doc['original_filename']}")
                    print(f"    텍스트 추출: {'있음' if doc.get('extracted_text') else '없음'}")
                    print(f"    분석 결과: {'있음' if doc.get('analysis_result') else '없음'}")
                    
                    # 3. 분석 결과 조회 테스트
                    if doc.get('analysis_result'):
                        try:
                            analysis_response = await client.get(f"{base_url}/api/documents/{doc['id']}/analysis")
                            if analysis_response.status_code == 200:
                                print(f"    ✅ 분석 결과 조회 성공")
                            else:
                                print(f"    ❌ 분석 결과 조회 실패: {analysis_response.status_code}")
                                print(f"    응답: {analysis_response.text}")
                        except Exception as e:
                            print(f"    ❌ 분석 결과 조회 오류: {e}")
                    else:
                        print(f"    ⚠️ 분석 결과 없음 - 분석을 수행해야 함")
                        
                        # 4. 분석이 안된 문서가 있으면 간단한 분석 테스트
                        if doc.get('extracted_text'):
                            print(f"    🤖 테스트 분석 수행 중...")
                            try:
                                analysis_request = {
                                    "document_ids": [doc['id']],
                                    "user_intent": "문서 요약",
                                    "ai_model": "local",
                                    "additional_context": "",
                                    "user_consent": False
                                }
                                
                                analysis_response = await client.post(
                                    f"{base_url}/api/documents/analyze",
                                    json=analysis_request
                                )
                                
                                if analysis_response.status_code == 200:
                                    print(f"    ✅ 분석 성공!")
                                    result = analysis_response.json()
                                    print(f"    키워드: {result.get('keywords', [])}")
                                    print(f"    문서 유형: {result.get('document_type', 'Unknown')}")
                                else:
                                    print(f"    ❌ 분석 실패: {analysis_response.status_code}")
                                    print(f"    오류: {analysis_response.text}")
                                    
                            except Exception as e:
                                print(f"    ❌ 분석 오류: {e}")
                    
                    print()  # 빈 줄
                    
            else:
                print(f"❌ 문서 목록 조회 실패: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 문서 목록 조회 오류: {e}")

if __name__ == "__main__":
    asyncio.run(test_analysis_flow()) 