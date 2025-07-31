#!/usr/bin/env python3
"""
간단한 종합 분석 테스트 (의존성 최소화)
"""
import re
from collections import Counter

def extract_keywords(text, num_keywords=10):
    """간단한 키워드 추출"""
    # 특수문자 제거 및 단어 분리
    words = re.findall(r'\b[가-힣a-zA-Z]{2,}\b', text)
    
    # 불용어 제거
    stopwords = {
        '그리고', '하지만', '그런데', '그래서', '따라서', '또한', '그러나', '이것', '그것', '저것',
        '있다', '없다', '이다', '아니다', '하다', '되다', '같다', '다른', '많은', '작은', '큰',
        'and', 'but', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did'
    }
    
    filtered_words = [word.lower() for word in words if word.lower() not in stopwords and len(word) > 2]
    
    # 빈도 계산
    word_freq = Counter(filtered_words)
    
    # 상위 키워드 반환
    keywords = [word for word, freq in word_freq.most_common(num_keywords)]
    
    return keywords

def classify_document_type(text):
    """문서 유형 분류"""
    text_lower = text.lower()
    
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
    else:
        return '일반 문서'

def generate_interview_recommendations(doc_types, keywords):
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
                    ['react', 'javascript', 'python', 'node', 'sql', 'aws', 'docker', 'git'])]
    
    if tech_keywords:
        recommendations.append(f"주요 기술 스택({', '.join(tech_keywords[:3])})에 대한 심화 질문을 준비하세요")
    
    # 기본 추천사항
    recommendations.extend([
        "자기소개를 1분, 3분, 5분 버전으로 각각 준비하세요",
        "지원 동기와 회사에 대한 이해도를 명확히 표현할 수 있어야 합니다",
        "향후 커리어 계획과 성장 목표를 구체적으로 준비하세요"
    ])
    
    return recommendations[:8]

def generate_interview_questions(doc_types, keywords):
    """면접 예상 질문 생성"""
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
    
    return questions[:15]

def analyze_document_relationships(doc_types):
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

def comprehensive_analysis(texts, user_intent="면접 준비"):
    """종합 분석 수행"""
    print(f"🎯 {user_intent} 종합 분석")
    print("=" * 50)
    
    # 문서 유형 분류
    doc_types = [classify_document_type(text) for text in texts]
    
    # 전체 텍스트 통합
    combined_text = "\n\n".join(texts)
    
    # 각 문서별 키워드 추출
    all_keywords = []
    for text in texts:
        keywords = extract_keywords(text, 8)
        all_keywords.extend(keywords)
    
    # 중복 제거 및 빈도순 정렬
    keyword_counts = Counter(all_keywords)
    top_keywords = [word for word, count in keyword_counts.most_common(15)]
    
    # 문서별 분석
    doc_analysis = {}
    for i, (text, doc_type) in enumerate(zip(texts, doc_types)):
        doc_analysis[f"문서{i+1}"] = {
            "type": doc_type,
            "keywords": extract_keywords(text, 5),
            "summary": text[:200] + "..." if len(text) > 200 else text
        }
    
    # 면접 준비 특화 분석
    if user_intent == "면접 준비":
        recommendations = generate_interview_recommendations(doc_types, top_keywords)
        interview_questions = generate_interview_questions(doc_types, top_keywords)
    else:
        recommendations = [
            "문서들의 주요 키워드를 파악했습니다",
            "문서 간 연관성을 검토해보세요",
            "핵심 내용을 요약하여 정리하세요"
        ]
        interview_questions = []
    
    # 문서 간 연관성 분석
    relationships = analyze_document_relationships(doc_types)
    
    return {
        "document_type": f"다중문서 ({', '.join(set(doc_types))})",
        "keywords": top_keywords,
        "main_topics": list(set([kw for kw in top_keywords[:5]])),
        "summary": f"총 {len(texts)}개의 문서가 분석되었습니다. 문서 구성: {', '.join([f'{dtype} 1개' for dtype in set(doc_types)])}",
        "recommendations": recommendations,
        "interview_questions": interview_questions,
        "document_analysis": doc_analysis,
        "document_relationships": relationships,
        "total_documents": len(texts),
        "analysis_method": "종합 다중 문서 분석"
    }

def main():
    """메인 테스트 함수"""
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
            analysis = comprehensive_analysis(
                texts=test_case["texts"],
                user_intent=test_case["user_intent"]
            )
            
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
    main() 