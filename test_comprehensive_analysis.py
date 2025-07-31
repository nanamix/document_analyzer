#!/usr/bin/env python3
"""
종합 분석 기능 테스트 스크립트
"""
import sys
import os
import asyncio

# 백엔드 경로를 sys.path에 추가
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# 현재 디렉토리도 추가 (config.py 접근용)
sys.path.insert(0, os.path.dirname(__file__))

from app.services.ai_analyzer import ai_analyzer

async def test_comprehensive_analysis():
    """종합 분석 테스트"""
    print("🎯 면접 준비 종합 분석 테스트")
    print("=" * 50)
    
    # 테스트 문서들
    resume_text = """
    김개발 - 풀스택 개발자
    
    경력사항:
    - ABC 회사 (2021-2023): React, Node.js를 활용한 웹 서비스 개발
    - 사용자 경험 개선으로 서비스 만족도 30% 향상
    - 팀 리더로서 5명의 개발자와 협업
    
    기술스택:
    - Frontend: React, JavaScript, TypeScript, HTML/CSS
    - Backend: Node.js, Express, Python, Django
    - Database: MySQL, MongoDB
    - DevOps: Docker, AWS, Git
    
    프로젝트:
    - 전자상거래 플랫폼 개발 (React + Node.js)
    - 실시간 채팅 시스템 구현 (WebSocket)
    - RESTful API 설계 및 구현
    """
    
    assignment_text = """
    사전과제: 투두 리스트 애플리케이션
    
    요구사항:
    - React를 이용한 SPA 개발
    - 할 일 추가, 삭제, 완료 처리 기능
    - 로컬 스토리지를 이용한 데이터 저장
    
    구현 내용:
    - React Hooks(useState, useEffect) 활용
    - 컴포넌트 기반 설계
    - CSS Modules를 이용한 스타일링
    - TypeScript 적용으로 타입 안정성 확보
    
    기술적 고려사항:
    - 사용자 경험을 위한 로딩 상태 처리
    - 에러 바운더리 구현
    - 접근성(a11y) 고려한 UI 설계
    - 반응형 웹 디자인 적용
    
    성능 최적화:
    - React.memo를 이용한 불필요한 리렌더링 방지
    - useMemo, useCallback을 이용한 최적화
    - 번들 크기 최적화
    """
    
    portfolio_text = """
    개인 프로젝트 포트폴리오
    
    1. 실시간 코딩 테스트 플랫폼
    - 기술스택: React, Node.js, Socket.io, Docker
    - 실시간 코드 실행 및 채점 시스템
    - 사용자 인증 및 권한 관리
    - 배포: AWS EC2, RDS 활용
    
    2. 개인 블로그 플랫폼
    - 기술스택: Next.js, TypeScript, Prisma, PostgreSQL
    - SEO 최적화 및 SSR 구현
    - 댓글 시스템 및 검색 기능
    - 관리자 대시보드 개발
    
    3. 모바일 앱 개발
    - React Native를 이용한 크로스 플랫폼 앱
    - 푸시 알림 및 오프라인 기능
    - 앱스토어 배포 경험
    """
    
    # 테스트 케이스들
    test_cases = [
        {
            "name": "단일 문서 (이력서만)",
            "texts": [resume_text],
            "user_intent": "면접 준비"
        },
        {
            "name": "다중 문서 (이력서 + 사전과제)",
            "texts": [resume_text, assignment_text],
            "user_intent": "면접 준비"
        },
        {
            "name": "전체 문서 (이력서 + 사전과제 + 포트폴리오)",
            "texts": [resume_text, assignment_text, portfolio_text],
            "user_intent": "면접 준비"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}️⃣ {test_case['name']}")
        print("-" * 30)
        
        try:
            result = await ai_analyzer.analyze_documents(
                texts=test_case["texts"],
                user_intent=test_case["user_intent"],
                ai_model="local",
                additional_context="개발자 포지션 면접 준비"
            )
            
            analysis = result["analysis"]
            
            print(f"✅ 분석 완료!")
            print(f"📄 문서 유형: {analysis.get('document_type', 'Unknown')}")
            print(f"📊 키워드 수: {len(analysis.get('keywords', []))}")
            print(f"🔑 주요 키워드: {', '.join(analysis.get('keywords', [])[:5])}")
            print(f"❓ 면접 질문 수: {len(analysis.get('interview_questions', []))}")
            print(f"💡 추천사항 수: {len(analysis.get('recommendations', []))}")
            
            # 문서별 분석 결과
            if analysis.get('document_analysis'):
                print(f"📁 문서별 분석: {len(analysis['document_analysis'])}개 문서")
                for doc_key, doc_data in analysis['document_analysis'].items():
                    print(f"  - {doc_key}: {doc_data['type']}")
            
            # 문서 간 연관성
            if analysis.get('document_relationships'):
                print(f"🔗 연관성 분석: {len(analysis['document_relationships'])}개 관계")
                for rel_key in analysis['document_relationships'].keys():
                    print(f"  - {rel_key}")
            
            # 샘플 면접 질문 표시
            if analysis.get('interview_questions'):
                print(f"\n📝 면접 질문 예시:")
                for j, question in enumerate(analysis['interview_questions'][:3], 1):
                    print(f"  Q{j}. {question}")
                if len(analysis['interview_questions']) > 3:
                    print(f"  ... 총 {len(analysis['interview_questions'])}개 질문")
            
        except Exception as e:
            print(f"❌ 분석 실패: {e}")
            import traceback
            traceback.print_exc()
        
        print()

if __name__ == "__main__":
    print("종합 분석 기능 테스트 시작...")
    print(f"Python path: {sys.path[:3]}")
    
    try:
        asyncio.run(test_comprehensive_analysis())
        print("테스트 완료!")
    except KeyboardInterrupt:
        print("\n테스트 중단됨")
    except Exception as e:
        print(f"테스트 실행 중 오류: {e}")
        import traceback
        traceback.print_exc() 