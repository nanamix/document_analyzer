#!/bin/bash

# Document Analyzer 의존성 설치 스크립트 (macOS 최적화)

echo "📄 Document Analyzer 의존성 설치 (macOS 우선)"
echo "=================================================="

# OS 감지
OS=""
ARCH=""
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    # Apple Silicon vs Intel Mac 구분
    if [[ $(uname -m) == "arm64" ]]; then
        ARCH="apple_silicon"
        HOMEBREW_PREFIX="/opt/homebrew"
    else
        ARCH="intel"
        HOMEBREW_PREFIX="/usr/local"
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OS="windows"
else
    echo "⚠️  지원하지 않는 운영체제입니다: $OSTYPE"
fi

echo "🖥️  운영체제: $OS"
if [[ "$OS" == "macos" ]]; then
    echo "💻 Mac 아키텍처: $ARCH"
    echo "🍺 Homebrew 경로: $HOMEBREW_PREFIX"
fi

# Python 설치 확인
echo "🔍 Python 설치 상태 확인..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3가 설치되지 않았습니다."
    if [[ "$OS" == "macos" ]]; then
        echo "macOS에서 Python 설치 방법:"
        echo "  🍺 Homebrew: brew install python"
        echo "  🌐 공식 사이트: https://www.python.org/"
        echo ""
        if command -v brew &> /dev/null; then
            read -p "Homebrew로 Python을 설치하시겠습니까? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                brew install python
            fi
        fi
    else
        echo "Python 3.8 이상을 설치해주세요: https://www.python.org/"
    fi
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python 버전: $PYTHON_VERSION"

# Node.js 설치 확인
echo "🔍 Node.js 설치 상태 확인..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js가 설치되지 않았습니다."
    if [[ "$OS" == "macos" ]]; then
        echo "macOS에서 Node.js 설치 방법:"
        echo "  🍺 Homebrew: brew install node"
        echo "  📦 NVM: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
        echo "  🌐 공식 사이트: https://nodejs.org/"
        echo ""
        if command -v brew &> /dev/null; then
            read -p "Homebrew로 Node.js를 설치하시겠습니까? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                brew install node
            fi
        fi
    else
        echo "Node.js 16 이상을 설치해주세요: https://nodejs.org/"
    fi
    exit 1
fi

NODE_VERSION=$(node -v)
echo "✅ Node.js 버전: $NODE_VERSION"

# Tesseract OCR 설치 안내
echo "🔍 Tesseract OCR 설치 상태 확인..."
if ! command -v tesseract &> /dev/null; then
    echo "⚠️  Tesseract OCR가 설치되지 않았습니다."
    echo ""
    
    if [[ "$OS" == "macos" ]]; then
        echo "📋 macOS Tesseract OCR 설치 방법:"
        echo "  🍺 Homebrew (권장):"
        echo "    brew install tesseract tesseract-lang"
        echo ""
        echo "  📦 MacPorts:"
        echo "    sudo port install tesseract +langpack_korean"
        echo ""
        
        if command -v brew &> /dev/null; then
            read -p "Homebrew로 Tesseract를 지금 설치하시겠습니까? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                echo "🔄 Tesseract 설치 중..."
                brew install tesseract tesseract-lang
                
                # 설치 후 경로 확인 및 .env 파일 업데이트
                TESSERACT_PATH=$(which tesseract)
                echo "✅ Tesseract 설치 완료: $TESSERACT_PATH"
                
                # .env 파일 업데이트
                if [ -f "backend/.env" ]; then
                    sed -i '' "s|TESSERACT_CMD=.*|TESSERACT_CMD=$TESSERACT_PATH|" backend/.env
                    echo "✅ .env 파일의 Tesseract 경로 업데이트 완료"
                fi
            fi
        else
            echo "❌ Homebrew가 설치되지 않았습니다."
            echo "   https://brew.sh/ 에서 Homebrew를 먼저 설치해주세요."
        fi
    elif [[ "$OS" == "linux" ]]; then
        echo "  🐧 Ubuntu/Debian:"
        echo "    sudo apt update"
        echo "    sudo apt install tesseract-ocr tesseract-ocr-kor"
        echo ""
        echo "  🎩 CentOS/RHEL:"
        echo "    sudo yum install tesseract tesseract-langpack-kor"
        echo ""
        read -p "Ubuntu/Debian 시스템에서 지금 설치하시겠습니까? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sudo apt update && sudo apt install -y tesseract-ocr tesseract-ocr-kor
        fi
    elif [[ "$OS" == "windows" ]]; then
        echo "  🪟 Windows:"
        echo "    https://github.com/UB-Mannheim/tesseract/wiki"
        echo "    에서 설치 파일을 다운로드하여 설치해주세요."
    fi
else
    TESSERACT_VERSION=$(tesseract --version | head -n1)
    TESSERACT_PATH=$(which tesseract)
    echo "✅ $TESSERACT_VERSION"
    echo "📍 Tesseract 경로: $TESSERACT_PATH"
fi

echo ""
echo "--------------------------------------------------"

# 백엔드 의존성 설치
echo "📦 백엔드 의존성 설치..."
if [ -f "backend/requirements.txt" ]; then
    cd backend
    
    # 가상환경 생성 및 활성화 권장
    if [ ! -d "venv" ]; then
        echo "🐍 Python 가상환경을 생성합니다..."
        python3 -m venv venv
        echo "✅ 가상환경이 생성되었습니다."
    fi
    
    echo "💡 가상환경 활성화 방법:"
    if [[ "$OS" == "windows" ]]; then
        echo "   backend\\venv\\Scripts\\activate"
    else
        echo "   source backend/venv/bin/activate"
    fi
    echo ""
    
    # 의존성 설치
    echo "📦 Python 패키지 설치 중..."
    if [[ "$OS" == "windows" ]]; then
        echo "venv/Scripts/activate && pip install -r requirements.txt"
    else
        source venv/bin/activate 2>/dev/null || true
        pip install --upgrade pip
        pip install -r requirements.txt
    fi
    
    if [ $? -eq 0 ]; then
        echo "✅ 백엔드 의존성 설치 완료"
    else
        echo "❌ 백엔드 의존성 설치 실패"
        echo "   수동으로 설치해주세요:"
        echo "   cd backend && source venv/bin/activate && pip install -r requirements.txt"
    fi
    
    cd ..
else
    echo "❌ backend/requirements.txt 파일이 없습니다."
fi

# 프론트엔드 의존성 설치
echo "📦 프론트엔드 의존성 설치..."
if [ -f "frontend/package.json" ]; then
    cd frontend
    
    # npm 또는 yarn 선택 (macOS에서는 성능상 yarn 추천)
    if command -v yarn &> /dev/null; then
        echo "🧶 Yarn을 사용하여 설치합니다..."
        yarn install
    else
        echo "📦 npm을 사용하여 설치합니다..."
        if [[ "$OS" == "macos" ]]; then
            echo "💡 성능 향상을 위해 Yarn 설치를 권장합니다: npm install -g yarn"
        fi
        npm install
    fi
    
    if [ $? -eq 0 ]; then
        echo "✅ 프론트엔드 의존성 설치 완료"
    else
        echo "❌ 프론트엔드 의존성 설치 실패"
    fi
    
    cd ..
else
    echo "❌ frontend/package.json 파일이 없습니다."
fi

echo ""
echo "--------------------------------------------------"
echo "🎉 의존성 설치가 완료되었습니다! (macOS 최적화)"
echo ""
echo "📋 다음 단계:"
echo "1. API 키 설정:"
echo "   cp backend/.env.example backend/.env"
echo "   # backend/.env 파일에서 API 키를 설정하세요"
echo ""

if [[ "$OS" == "macos" ]]; then
    echo "2. macOS 최적화 설정:"
    echo "   # Tesseract 경로가 자동으로 설정되었습니다"
    if [[ "$ARCH" == "apple_silicon" ]]; then
        echo "   # Apple Silicon Mac 감지됨 - /opt/homebrew 경로 사용"
    else
        echo "   # Intel Mac 감지됨 - /usr/local 경로 사용"
    fi
    echo ""
fi

echo "3. 서버 실행:"
echo "   python run_backend.py    # 백엔드 서버"
echo "   ./run_frontend.sh        # 프론트엔드 서버"
echo "   # 또는"
echo "   ./run.sh                 # 전체 실행 (권장)"
echo ""
echo "4. 브라우저에서 접속:"
echo "   http://localhost:3000"
echo ""

# 실행 권한 부여
chmod +x run_frontend.sh
chmod +x run_backend.py
chmod +x run.sh

echo "✅ 실행 스크립트에 실행 권한이 부여되었습니다."

if [[ "$OS" == "macos" ]]; then
    echo ""
    echo "🍎 macOS 사용자를 위한 추가 팁:"
    echo "  • Visual Studio Code 확장: Python, ES7+ React/Redux/React-Native snippets"
    echo "  • 터미널: iTerm2 + Oh My Zsh 추천"
    echo "  • 패키지 관리: Homebrew 사용 권장"
    echo "  • Docker Desktop for Mac (선택사항)"
fi 