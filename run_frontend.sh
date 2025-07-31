#!/bin/bash

# Document Analyzer Frontend 실행 스크립트 (macOS 최적화)

echo "📱 Document Analyzer Frontend (macOS 최적화)"
echo "=================================================="

# macOS 감지 및 아키텍처 확인
if [[ "$OSTYPE" == "darwin"* ]]; then
    if [[ $(uname -m) == "arm64" ]]; then
        echo "🍎 Apple Silicon Mac 감지됨"
        HOMEBREW_PREFIX="/opt/homebrew"
    else
        echo "💻 Intel Mac 감지됨"
        HOMEBREW_PREFIX="/usr/local"
    fi
    echo "🍺 Homebrew 경로: $HOMEBREW_PREFIX"
fi

# 현재 디렉토리 확인
if [ ! -d "frontend" ]; then
    echo "❌ frontend 디렉토리가 없습니다."
    echo "프로젝트 루트 디렉토리에서 실행해주세요."
    exit 1
fi

# Node.js 버전 확인
if ! command -v node &> /dev/null; then
    echo "❌ Node.js가 설치되지 않았습니다."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "🍺 macOS에서 Node.js 설치:"
        echo "   brew install node"
        echo "   또는 https://nodejs.org/ 에서 다운로드"
    else
        echo "Node.js 18 이상을 설치해주세요: https://nodejs.org/"
    fi
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    echo "❌ Node.js 16 이상이 필요합니다."
    echo "현재 버전: $(node -v)"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "🍺 업그레이드: brew upgrade node"
    fi
    exit 1
fi

echo "✅ Node.js 버전: $(node -v)"

# Yarn 설치 권장 (macOS 성능 최적화)
if [[ "$OSTYPE" == "darwin"* ]] && ! command -v yarn &> /dev/null; then
    echo "💡 macOS에서 성능 향상을 위해 Yarn 설치를 권장합니다."
    read -p "Yarn을 설치하시겠습니까? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v brew &> /dev/null; then
            brew install yarn
        else
            npm install -g yarn
        fi
    fi
fi

# 프론트엔드 디렉토리로 이동
cd frontend

# .env 파일 확인
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "⚠️  .env 파일이 없습니다."
    read -p ".env.example을 복사하여 .env 파일을 생성하시겠습니까? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env
        echo "✅ .env 파일이 생성되었습니다."
    fi
fi

# package.json 확인
if [ ! -f "package.json" ]; then
    echo "❌ package.json 파일이 없습니다."
    exit 1
fi

# node_modules 확인 및 설치
if [ ! -d "node_modules" ]; then
    echo "📦 패키지를 설치합니다..."
    
    # npm 또는 yarn 감지 (macOS에서는 yarn 우선)
    if command -v yarn &> /dev/null; then
        echo "🧶 Yarn을 사용합니다 (macOS 최적화)..."
        yarn install
    else
        echo "📦 npm을 사용합니다..."
        npm install
    fi
    
    if [ $? -ne 0 ]; then
        echo "❌ 패키지 설치에 실패했습니다."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            echo "🍎 macOS 문제 해결:"
            echo "   1. Xcode Command Line Tools: xcode-select --install"
            echo "   2. Node.js 재설치: brew reinstall node"
            echo "   3. 캐시 정리: npm cache clean --force"
        fi
        exit 1
    fi
    
    echo "✅ 패키지 설치가 완료되었습니다."
else
    echo "✅ node_modules가 존재합니다."
fi

# 백엔드 서버 확인 - 포트 4000으로 변경
echo "🔍 백엔드 서버 연결을 확인합니다..."
BACKEND_URL="http://localhost:4000"

if curl -s "$BACKEND_URL/health" > /dev/null; then
    echo "✅ 백엔드 서버가 실행 중입니다."
else
    echo "⚠️  백엔드 서버에 연결할 수 없습니다."
    echo "   백엔드 서버를 먼저 실행해주세요:"
    echo "   python run_backend.py"
    echo ""
    echo "   또는 전체 실행:"
    echo "   ./run.sh"
fi

# macOS에서 포트 확인 - 포트 4001로 변경
if [[ "$OSTYPE" == "darwin"* ]]; then
    if lsof -ti:4001 >/dev/null 2>&1; then
        echo "⚠️  포트 4001이 이미 사용 중입니다."
        echo "사용 중인 프로세스를 종료하거나 다른 포트를 사용하세요."
        read -p "계속 진행하시겠습니까? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

echo "--------------------------------------------------"
echo "🚀 프론트엔드 서버를 시작합니다..."
echo "   URL: http://localhost:4001"
echo "   종료하려면 Ctrl+C를 누르세요."

if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 macOS에서 실행 중..."
    echo "   💡 브라우저가 자동으로 열립니다."
fi

# 개발 서버 시작 - 포트 4001 설정
if command -v yarn &> /dev/null && [ -f "yarn.lock" ]; then
    yarn start
else
    npm start
fi 