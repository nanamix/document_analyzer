#!/bin/bash

# Document Analyzer 통합 실행 스크립트 (macOS 최적화) 🔒 보안 우선

echo "🚀 Document Analyzer 통합 실행 (macOS 최적화)"
echo "🔒 보안 우선: 기본적으로 로컬 분석만 활성화됨"
echo "========================================================="

# macOS 감지
if [[ "$OSTYPE" == "darwin"* ]]; then
    if [[ $(uname -m) == "arm64" ]]; then
        echo "🍎 Apple Silicon Mac 감지됨"
    else
        echo "💻 Intel Mac 감지됨"
    fi
fi

# 정리 함수
cleanup() {
    echo ""
    echo "🛑 애플리케이션을 종료합니다..."
    
    # 백그라운드 프로세스 종료
    if [ ! -z "$BACKEND_PID" ]; then
        echo "📄 백엔드 서버 종료 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        echo "📱 프론트엔드 서버 종료 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null
    fi
    
    # 포트 확인 및 정리 - 4000, 4001로 변경
    if [[ "$OSTYPE" == "darwin"* ]]; then
        BACKEND_PORT_PID=$(lsof -ti:4000 2>/dev/null)
        FRONTEND_PORT_PID=$(lsof -ti:4001 2>/dev/null)
        
        if [ ! -z "$BACKEND_PORT_PID" ]; then
            echo "🔧 포트 4000 정리 중..."
            kill -9 $BACKEND_PORT_PID 2>/dev/null
        fi
        
        if [ ! -z "$FRONTEND_PORT_PID" ]; then
            echo "🔧 포트 4001 정리 중..."
            kill -9 $FRONTEND_PORT_PID 2>/dev/null
        fi
    fi
    
    echo "✅ 정상적으로 종료되었습니다."
    exit 0
}

# Ctrl+C 처리
trap cleanup SIGINT SIGTERM

# .env 파일 확인
if [ ! -f "backend/.env" ]; then
    echo "⚠️  backend/.env 파일이 없습니다."
    if [ -f "backend/.env.example" ]; then
        echo "📋 .env.example을 복사하여 .env 파일을 생성합니다..."
        cp backend/.env.example backend/.env
        echo "✅ .env 파일이 생성되었습니다."
        echo "🔒 기본값으로 로컬 분석만 활성화됩니다."
    else
        echo "❌ .env.example 파일이 없습니다."
        exit 1
    fi
fi

# 의존성 확인
echo "🔍 의존성을 확인합니다..."
if [ ! -f "backend/requirements.txt" ] || [ ! -f "frontend/package.json" ]; then
    echo "❌ 필수 파일이 없습니다. install_dependencies.sh를 먼저 실행해주세요."
    exit 1
fi

# Python 가상환경 확인
if [ ! -d "backend/venv" ]; then
    echo "⚠️  Python 가상환경이 없습니다."
    echo "📦 ./install_dependencies.sh를 실행하여 설정을 완료해주세요."
    exit 1
fi

# Node.js 모듈 확인
if [ ! -d "frontend/node_modules" ]; then
    echo "⚠️  Node.js 모듈이 설치되지 않았습니다."
    echo "📦 ./install_dependencies.sh를 실행하여 설정을 완료해주세요."
    exit 1
fi

echo "✅ 모든 의존성이 준비되었습니다."
echo ""

# 백엔드 서버 시작 - 포트 4000
echo "🔧 백엔드 서버를 시작합니다 (포트 4000)..."
cd backend
source venv/bin/activate 2>/dev/null || true
uvicorn app.main:app --host 0.0.0.0 --port 4000 --reload > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

echo "📄 백엔드 서버 시작됨 (PID: $BACKEND_PID)"

# 백엔드 서버 준비 대기
echo "⏳ 백엔드 서버 준비 중..."
for i in {1..30}; do
    if curl -s http://localhost:4000/health > /dev/null 2>&1; then
        echo "✅ 백엔드 서버가 준비되었습니다!"
        break
    fi
    sleep 1
    echo -n "."
done

if ! curl -s http://localhost:4000/health > /dev/null 2>&1; then
    echo ""
    echo "❌ 백엔드 서버 시작에 실패했습니다."
    echo "📋 로그를 확인하세요: cat backend.log"
    cleanup
fi

echo ""

# 프론트엔드 서버 시작 - 포트 4001
echo "🎨 프론트엔드 서버를 시작합니다 (포트 4001)..."
cd frontend

# 포트 환경변수 설정
export PORT=4001

if command -v yarn &> /dev/null && [ -f "yarn.lock" ]; then
    yarn start > ../frontend.log 2>&1 &
else
    npm start > ../frontend.log 2>&1 &
fi

FRONTEND_PID=$!
cd ..

echo "📱 프론트엔드 서버 시작됨 (PID: $FRONTEND_PID)"

# 프론트엔드 서버 준비 대기
echo "⏳ 프론트엔드 서버 준비 중..."
for i in {1..60}; do
    if curl -s http://localhost:4001 > /dev/null 2>&1; then
        echo "✅ 프론트엔드 서버가 준비되었습니다!"
        break
    fi
    sleep 1
    echo -n "."
done

echo ""
echo "========================================================="
echo "🎉 Document Analyzer가 성공적으로 시작되었습니다!"
echo ""
echo "📱 프론트엔드: http://localhost:4001"
echo "📄 백엔드 API: http://localhost:4000"
echo "📚 API 문서: http://localhost:4000/docs"
echo "🔒 보안 상태: http://localhost:4000/api/documents/security/status"
echo ""
echo "🔒 보안 우선 모드:"
echo "   ✅ 로컬 분석만 활성화"
echo "   ✅ 외부 AI 비활성화"
echo "   ✅ 데이터 외부 전송 차단"
echo ""

# macOS에서 브라우저 자동 열기
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 macOS에서 브라우저를 자동으로 엽니다..."
    sleep 2
    open http://localhost:4001
fi

echo "📋 사용법:"
echo "   • 문서 업로드: PDF, PNG, JPG 지원"
echo "   • 분석 방법: 로컬 분석 (기본값)"
echo "   • 면접 준비: 예상 질문 자동 생성"
echo "   • 안전 보장: 문서 내용 외부 전송 없음"
echo ""
echo "🛑 종료하려면 Ctrl+C를 누르세요"
echo "========================================================="

# 서버들이 종료될 때까지 대기
wait 