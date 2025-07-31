#!/usr/bin/env python3
"""
분석 결과 디버깅 스크립트 (urllib 사용)
"""
import urllib.request
import urllib.parse
import json
import sys

def make_request(url, method='GET', data=None):
    """HTTP 요청 수행"""
    try:
        if data:
            data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=data, method=method)
            req.add_header('Content-Type', 'application/json')
        else:
            req = urllib.request.Request(url, method=method)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status, response.read().decode('utf-8')
    except Exception as e:
        return None, str(e)

def test_analysis_flow():
    """분석 플로우 테스트"""
    base_url = "http://localhost:4000"
    
    print("🔍 문서 분석 플로우 디버깅")
    print("=" * 50)
    
    # 1. 서버 상태 확인
    print("1️⃣ 서버 상태 확인 중...")
    status, response = make_request(f"{base_url}/health")
    
    if status != 200:
        print(f"❌ 백엔드 서버 연결 실패: {response}")
        print("💡 백엔드 서버가 실행 중인지 확인하세요!")
        return
    
    print("✅ 백엔드 서버 연결 성공")
    
    # 2. 문서 목록 조회
    print("\n2️⃣ 문서 목록 조회 중...")
    status, response = make_request(f"{base_url}/api/documents/")
    
    if status != 200:
        print(f"❌ 문서 목록 조회 실패: {response}")
        return
    
    try:
        documents = json.loads(response)
        print(f"📄 문서 목록: {len(documents)}개 문서 발견")
        
        if not documents:
            print("⚠️ 업로드된 문서가 없습니다.")
            print("💡 먼저 문서를 업로드해주세요!")
            return
        
        for doc in documents:
            print(f"\n  - ID {doc['id']}: {doc['original_filename']}")
            print(f"    파일 크기: {doc.get('file_size', 0)} bytes")
            print(f"    텍스트 추출: {'있음' if doc.get('extracted_text') else '없음'}")
            print(f"    분석 결과: {'있음' if doc.get('analysis_result') else '없음'}")
            
            # 3. 분석 결과 조회 테스트
            print(f"    🔍 분석 결과 조회 테스트 중...")
            analysis_status, analysis_response = make_request(f"{base_url}/api/documents/{doc['id']}/analysis")
            
            if analysis_status == 200:
                print(f"    ✅ 분석 결과 조회 성공!")
                try:
                    analysis_data = json.loads(analysis_response)
                    if isinstance(analysis_data, dict):
                        print(f"    📊 키워드: {analysis_data.get('keywords', [])}")
                        print(f"    📄 문서 유형: {analysis_data.get('document_type', 'Unknown')}")
                    else:
                        print(f"    📋 분석 결과 타입: {type(analysis_data)}")
                except json.JSONDecodeError:
                    print(f"    ⚠️ JSON 파싱 오류")
                    
            elif analysis_status == 404:
                print(f"    ❌ 분석 결과 없음 (404 Not Found)")
                print(f"    💡 이 문서는 아직 분석되지 않았습니다!")
                
                # 4. 분석이 안된 문서면 간단한 분석 테스트
                if doc.get('extracted_text'):
                    print(f"    🤖 테스트 분석 수행 중...")
                    analysis_request = {
                        "document_ids": [doc['id']],
                        "user_intent": "문서 요약",
                        "ai_model": "local",
                        "additional_context": "",
                        "user_consent": False
                    }
                    
                    test_status, test_response = make_request(
                        f"{base_url}/api/documents/analyze",
                        method='POST',
                        data=analysis_request
                    )
                    
                    if test_status == 200:
                        print(f"    ✅ 분석 성공!")
                        try:
                            result = json.loads(test_response)
                            print(f"    키워드: {result.get('keywords', [])}")
                            print(f"    문서 유형: {result.get('document_type', 'Unknown')}")
                        except json.JSONDecodeError:
                            print(f"    ⚠️ 분석 결과 JSON 파싱 오류")
                    else:
                        print(f"    ❌ 분석 실패 ({test_status}): {test_response}")
                else:
                    print(f"    ⚠️ 텍스트 추출이 안되어 분석할 수 없습니다")
            else:
                print(f"    ❌ 분석 결과 조회 실패 ({analysis_status}): {analysis_response}")
        
    except json.JSONDecodeError:
        print(f"❌ JSON 파싱 오류: {response}")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

def main():
    """메인 함수"""
    print("Document Analyzer 디버깅 도구")
    print("httpx 없이 urllib 사용")
    print()
    
    try:
        test_analysis_flow()
    except KeyboardInterrupt:
        print("\n중단됨")
    except Exception as e:
        print(f"예상치 못한 오류: {e}")

if __name__ == "__main__":
    main() 