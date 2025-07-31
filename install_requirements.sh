#!/bin/bash
# Document Analyzer 의존성 설치 스크립트

echo "🔧 Document Analyzer 의존성 설치"
echo "================================"

# 현재 디렉토리 확인
if [ ! -f "backend/requirements.txt" ]; then
    echo "❌ backend/requirements.txt 파일을 찾을 수 없습니다."
    echo "프로젝트 루트 디렉토리에서 실행해주세요."
    exit 1
fi

# Python 가상환경 확인
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️ 가상환경이 활성화되지 않았습니다."
    echo "가상환경 생성 및 활성화를 진행합니다..."
    
    # 가상환경 생성
    python3 -m venv venv
    
    # 가상환경 활성화 (OS별 분기)
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    echo "✅ 가상환경 활성화 완료"
else
    echo "✅ 가상환경이 이미 활성화되어 있습니다: $VIRTUAL_ENV"
fi

# pip 업그레이드
echo "🔄 pip 업그레이드 중..."
pip install --upgrade pip

# 백엔드 의존성 설치
echo "📦 백엔드 의존성 설치 중..."
pip install -r backend/requirements.txt

# 프론트엔드 의존성 확인
if [ -f "frontend/package.json" ]; then
    echo "📦 프론트엔드 의존성 설치 중..."
    cd frontend
    
    # npm 또는 yarn 확인
    if command -v yarn &> /dev/null; then
        echo "Using yarn..."
        yarn install
    elif command -v npm &> /dev/null; then
        echo "Using npm..."
        npm install
    else
        echo "❌ npm 또는 yarn이 설치되지 않았습니다."
        echo "Node.js를 설치해주세요."
    fi
    
    cd ..
fi

echo
echo "✅ 의존성 설치 완료!"
echo
echo "🚀 서버 실행 방법:"
echo "  백엔드: python run_backend.py"
echo "  프론트엔드: ./run_frontend.sh"
echo "  또는: ./run.sh (전체 실행)" 