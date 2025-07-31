#!/bin/bash
# Document Analyzer API 테스트 스크립트

BASE_URL="http://localhost:4000"

echo "🔍 Document Analyzer API 테스트"
echo "=================================="

# 1. 서버 상태 확인
echo "1️⃣ 서버 상태 확인..."
curl -s "${BASE_URL}/health" | jq . 2>/dev/null || curl -s "${BASE_URL}/health"
echo

# 2. 문서 목록 조회
echo "2️⃣ 문서 목록 조회..."
DOCS_RESPONSE=$(curl -s "${BASE_URL}/api/documents/")
echo "$DOCS_RESPONSE" | jq . 2>/dev/null || echo "$DOCS_RESPONSE"
echo

# 3. 문서 ID 추출 (첫 번째 문서)
FIRST_DOC_ID=$(echo "$DOCS_RESPONSE" | jq -r '.[0].id' 2>/dev/null)

if [ "$FIRST_DOC_ID" != "null" ] && [ "$FIRST_DOC_ID" != "" ]; then
    echo "3️⃣ 첫 번째 문서 (ID: $FIRST_DOC_ID) 분석 결과 조회..."
    
    # 분석 결과 조회 시도
    ANALYSIS_RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" "${BASE_URL}/api/documents/${FIRST_DOC_ID}/analysis")
    HTTP_STATUS=$(echo "$ANALYSIS_RESPONSE" | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    BODY=$(echo "$ANALYSIS_RESPONSE" | sed -e 's/HTTPSTATUS:.*//g')
    
    echo "HTTP 상태 코드: $HTTP_STATUS"
    
    if [ "$HTTP_STATUS" = "200" ]; then
        echo "✅ 분석 결과 조회 성공!"
        echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
    elif [ "$HTTP_STATUS" = "404" ]; then
        echo "❌ 분석 결과 없음 (404 Not Found)"
        echo "💡 분석을 먼저 수행해야 합니다!"
        echo
        
        # 4. 분석 수행 테스트
        echo "4️⃣ 테스트 분석 수행..."
        ANALYSIS_REQUEST='{
            "document_ids": ['$FIRST_DOC_ID'],
            "user_intent": "문서 요약",
            "ai_model": "local",
            "additional_context": "",
            "user_consent": false
        }'
        
        ANALYZE_RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST \
            -H "Content-Type: application/json" \
            -d "$ANALYSIS_REQUEST" \
            "${BASE_URL}/api/documents/analyze")
            
        ANALYZE_STATUS=$(echo "$ANALYZE_RESPONSE" | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
        ANALYZE_BODY=$(echo "$ANALYZE_RESPONSE" | sed -e 's/HTTPSTATUS:.*//g')
        
        echo "분석 HTTP 상태 코드: $ANALYZE_STATUS"
        
        if [ "$ANALYZE_STATUS" = "200" ]; then
            echo "✅ 분석 성공!"
            echo "$ANALYZE_BODY" | jq . 2>/dev/null || echo "$ANALYZE_BODY"
            echo
            
            # 5. 분석 후 결과 재조회
            echo "5️⃣ 분석 후 결과 재조회..."
            curl -s "${BASE_URL}/api/documents/${FIRST_DOC_ID}/analysis" | jq . 2>/dev/null || \
            curl -s "${BASE_URL}/api/documents/${FIRST_DOC_ID}/analysis"
        else
            echo "❌ 분석 실패!"
            echo "$ANALYZE_BODY"
        fi
    else
        echo "❌ 예상치 못한 오류 (HTTP $HTTP_STATUS)"
        echo "$BODY"
    fi
else
    echo "⚠️ 업로드된 문서가 없습니다!"
    echo "💡 먼저 프론트엔드에서 문서를 업로드해주세요."
fi

echo
echo "===================="
echo "테스트 완료" 