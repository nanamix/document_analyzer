# 📄 Document Analyzer (macOS 최적화) 🔒 보안 우선

AI를 활용한 문서 분석 시스템으로, 업로드된 문서를 분석하여 키워드 추출, 내용 요약, 면접 예상 질문 생성 등의 기능을 제공합니다.

**🍎 macOS 사용자를 위한 최적화된 버전입니다!**

**🔒 보안 우선: 기본적으로 모든 분석은 로컬에서 수행되며, 문서 내용이 외부로 전송되지 않습니다.**

## 🛡️ 보안 특징

### ✅ 로컬 우선 분석
- **기본 설정**: 모든 분석이 로컬에서 수행
- **외부 전송 차단**: 문서 내용이 외부 AI 서버로 전송되지 않음
- **민감 정보 보호**: 자동 마스킹 기능 제공
- **사용자 동의**: 외부 AI 사용 시 명시적 동의 필요

### 🔒 보안 수준 (우선 순위)
1. **🟢 로컬 분석** - 가장 안전 (기본값)
2. **🟢 Ollama 로컬 AI** - 로컬 AI 모델 사용
3. **🟢 LM Studio 로컬 AI** - OpenAI 호환 로컬 AI
4. **🟡 외부 AI** - 사용자 동의 + 데이터 마스킹

## 🌟 주요 기능

- **📤 다중 문서 업로드**: PDF, PNG, JPG 파일 지원
- **🛡️ 로컬 분석**: 외부 전송 없는 안전한 분석
- **🤖 로컬 AI 지원**: Ollama, LM Studio 등 로컬 AI 모델 지원
- **🔍 키워드 추출**: 문서에서 주요 키워드 자동 추출
- **📝 내용 요약**: 문서 내용 요약
- **🎯 면접 준비**: 문서 기반 면접 예상 질문 생성
- **📊 분석 결과 시각화**: 직관적인 웹 인터페이스
- **🔒 OCR 지원**: 이미지 문서의 텍스트 추출

## 🏗️ 시스템 구조

```md
document_analyzer/
├── backend/                # FastAPI 백엔드
│   ├── app/
│   │   ├── api/            # API 엔드포인트
│   │   ├── models/         # 데이터 모델
│   │   └── services/       # 비즈니스 로직 (보안 강화)
│   ├── config.py           # 설정 파일 (보안 우선)
│   └── requirements.txt    # Python 의존성
├── frontend/               # React 프론트엔드
│   ├── src/
│   │   ├── components/     # React 컴포넌트 (보안 UI)
│   │   └── services/       # API 서비스
│   └── package.json        # Node.js 의존성
└── README.md
```

## 🚀 빠른 시작 (macOS) 🔒 보안 우선

### 1. 의존성 설치

```bash
# macOS 최적화 자동 설치 (Apple Silicon/Intel 자동 감지)
./install_dependencies.sh

# 또는 수동 설치
cd backend && pip install -r requirements.txt
cd ../frontend && npm install
```

### 2. 환경 설정 (보안 우선)

```bash
# 백엔드 환경 변수 설정 (로컬 분석 기본값)
cp backend/.env.example backend/.env
# 기본적으로 로컬 분석만 활성화됨 - 외부 AI 비활성화

# 프론트엔드 환경 변수 설정 (선택사항)
cp frontend/.env.example frontend/.env
```

### 3. 서버 실행

**한 번에 실행 (권장):**
```bash
./run.sh
```

**개별 실행:**
```bash
# 백엔드 서버 (macOS 최적화) - 포트 4000
python run_backend.py

# 프론트엔드 서버 (새 터미널) - 포트 4001
./run_frontend.sh
```

### 4. 접속

브라우저에서 `http://localhost:4001`으로 접속
- macOS에서는 브라우저가 자동으로 열립니다!
- **기본적으로 로컬 분석만 활성화됨**

## ⚙️ macOS 시스템 요구사항

### 필수 요구사항
- **macOS**: 10.15 (Catalina) 이상
- **Python**: 3.8 이상 (Homebrew 설치 권장)
- **Node.js**: 16 이상 (Homebrew 설치 권장)
- **Tesseract OCR**: 이미지 텍스트 추출용

### macOS별 최적화
- **Apple Silicon (M1/M2/M3)**: `/opt/homebrew` 경로 자동 설정
- **Intel Mac**: `/usr/local` 경로 자동 설정
- **성능 최적화**: Yarn 패키지 매니저 사용 권장

### AI API 키 (선택사항 - 외부 AI 사용 시)
⚠️ **주의**: API 키 설정 시 문서 내용이 외부 서버로 전송될 수 있습니다
- **OpenAI API Key**: GPT-4 사용 (사용자 동의 필요)
- **Anthropic API Key**: Claude 사용 (사용자 동의 필요)
- **DeepSeek API Key**: DeepSeek 모델 사용 (사용자 동의 필요)

### macOS 의존성 설치

**Homebrew 설치 (필수):**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**필수 패키지 설치:**
```bash
# Python, Node.js, Tesseract 한 번에 설치
brew install python node tesseract tesseract-lang

# 또는 개별 설치
brew install python
brew install node  
brew install tesseract tesseract-lang
```

**성능 최적화 패키지 (선택사항):**
```bash
# Yarn (npm보다 빠름)
brew install yarn

# iTerm2 (터미널 개선)
brew install --cask iterm2

# Visual Studio Code
brew install --cask visual-studio-code
```

## 🔧 보안 설정 (환경 변수)

### 기본 보안 설정 (.env) - macOS 기본값

```env
# 🔒 보안 설정 (데이터 보호 우선)
# 외부 AI 사용 여부 (기본값: false - 보안 우선)
ENABLE_EXTERNAL_AI=false
# 외부 AI 사용 시 명시적 동의 필요 여부 (기본값: true)
REQUIRE_EXPLICIT_CONSENT=true
# 민감한 정보 자동 마스킹 (기본값: true)
ENABLE_DATA_MASKING=true

# AI Model Settings (기본값: local - 가장 안전)
DEFAULT_AI_MODEL=local
OPENAI_MODEL=gpt-4
CLAUDE_MODEL=claude-3-sonnet-20240229

# 로컬 AI 설정 (Ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# LM Studio 설정 (OpenAI 호환 API)
LMSTUDIO_BASE_URL=http://localhost:1234
LMSTUDIO_MODEL=local-model

# ⚠️ 외부 AI API Keys (ENABLE_EXTERNAL_AI=true 시에만 사용)
# 주의: 이 키들을 설정하면 문서 내용이 외부 서버로 전송될 수 있습니다
OPENAI_API_KEY=sk-your-openai-api-key-here
ANTHROPIC_API_KEY=sk-ant-api03-your-claude-api-key-here
DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here

# OCR Settings (macOS 자동 감지)
# Apple Silicon: /opt/homebrew/bin/tesseract
# Intel Mac: /usr/local/bin/tesseract
TESSERACT_CMD=/opt/homebrew/bin/tesseract

# Server Settings - 충돌 방지 포트
HOST=0.0.0.0
PORT=4000
FRONTEND_PORT=4001
```

### 보안 수준별 설정

**🟢 최고 보안 (기본값)**
```env
ENABLE_EXTERNAL_AI=false
DEFAULT_AI_MODEL=local
```

**🟡 중간 보안 (로컬 AI)**
```env
ENABLE_EXTERNAL_AI=false
DEFAULT_AI_MODEL=ollama
# Ollama 설치 필요: https://ollama.ai/
```

**🔴 주의 (외부 AI - 동의 필요)**
```env
ENABLE_EXTERNAL_AI=true
REQUIRE_EXPLICIT_CONSENT=true
ENABLE_DATA_MASKING=true
DEFAULT_AI_MODEL=openai
```

### 지원하는 파일 형식

- **PDF**: 텍스트 추출 및 OCR
- **이미지**: PNG, JPG, JPEG (OCR 처리)
- **최대 파일 크기**: 50MB

## 📋 API 문서

백엔드 서버 실행 후 다음 URL에서 API 문서 확인:
- **Swagger UI**: `http://localhost:4000/docs`
- **ReDoc**: `http://localhost:4000/redoc`
- **보안 상태**: `http://localhost:4000/api/documents/security/status`

### 주요 API 엔드포인트

- `POST /api/documents/upload` - 문서 업로드
- `GET /api/documents/` - 문서 목록 조회
- `POST /api/documents/analyze` - 문서 분석 (보안 강화)
- `GET /api/documents/{id}/analysis` - 분석 결과 조회
- `DELETE /api/documents/{id}` - 문서 삭제
- `GET /api/documents/security/status` - 보안 상태 확인

## 🎯 사용 사례

### 1. 📄 안전한 면접 준비 (기본값)
- 이력서와 자기소개서 업로드
- **로컬 분석**으로 예상 면접 질문 생성
- 키워드 기반 답변 준비
- ✅ **데이터 외부 전송 없음**

### 2. 🔒 기업 기밀 문서 분석
- 내부 문서의 핵심 내용 파악
- **완전 로컬 처리**로 보안 유지
- 주요 키워드 추출
- ✅ **기밀 정보 보호**

### 3. 🏠 개인 문서 관리
- 개인 문서의 주제 파악
- 핵심 개념 추출
- 빠른 내용 검토
- ✅ **개인정보 보호**

## 🛠️ macOS 개발 환경

### 개발 모드 실행

```bash
# 백엔드 (자동 재시작) - 포트 4000
python run_backend.py --reload

# 프론트엔드 (개발 서버) - 포트 4001
cd frontend && yarn start
```

### 권장 macOS 개발 도구

**터미널:**
```bash
# iTerm2 + Oh My Zsh
brew install --cask iterm2
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

**에디터:**
```bash
# VS Code + 확장
brew install --cask visual-studio-code
# 확장: Python, ES7+ React/Redux/React-Native snippets
```

**성능 모니터링:**
```bash
# 시스템 모니터링
brew install htop
brew install --cask stats
```

## 🐛 macOS 문제 해결

### 자주 발생하는 문제

1. **Tesseract 경로 오류**
   ```bash
   # Apple Silicon Mac
   export TESSERACT_CMD=/opt/homebrew/bin/tesseract
   
   # Intel Mac
   export TESSERACT_CMD=/usr/local/bin/tesseract
   ```

2. **Python 버전 충돌**
   ```bash
   # Homebrew Python 사용
   which python3
   brew install python
   ```

3. **Node.js 권한 오류**
   ```bash
   # NVM 사용 권장
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
   nvm install node
   ```

4. **포트 충돌**
   ```bash
   # 사용 중인 포트 확인
   lsof -ti:4000  # 백엔드
   lsof -ti:4001  # 프론트엔드
   
   # 다른 포트로 실행
   python run_backend.py --port 4002
   ```

5. **Xcode Command Line Tools**
   ```bash
   # 개발 도구 설치
   xcode-select --install
   ```

### 성능 최적화

```bash
# npm 캐시 정리
npm cache clean --force

# Yarn 사용 (더 빠름)
npm install -g yarn

# Python 가상환경 사용
python3 -m venv backend/venv
source backend/venv/bin/activate
```

## 🔒 보안 권장사항

### ✅ 권장 사용법
- **로컬 분석 우선 사용** (기본값)
- **기업 기밀 문서**: 외부 AI 절대 사용 금지
- **개인 문서**: 로컬 분석 또는 Ollama 사용
- **민감 정보 포함 문서**: 로컬 분석만 사용

### ⚠️ 주의사항
- 외부 AI 사용 시 **반드시 사용자 동의** 필요
- 민감한 정보는 **자동 마스킹**되지만 완전하지 않을 수 있음
- 외부 서비스의 개인정보 처리방침 확인 필요

### 🔧 보안 강화 방법
```bash
# 외부 AI 완전 비활성화
ENABLE_EXTERNAL_AI=false

# Ollama 로컬 AI 설치 (권장)
brew install ollama
ollama serve
ollama pull llama2

# LM Studio 설치 (대안)
# 1. https://lmstudio.ai 에서 다운로드
# 2. 원하는 모델 다운로드 (예: Llama 2, Mistral 등)
# 3. Local Server 탭에서 서버 시작
# 4. 포트를 1234로 설정 (기본값)
```

## 🐳 Docker 배포 (프로덕션)

### 🚀 빠른 Docker 배포

실제 서버 환경에서는 PostgreSQL과 Docker를 사용한 배포를 권장합니다:

```bash
# 1. 환경 설정
cp .env.production .env.production.local
nano .env.production.local  # 비밀번호 등 설정 수정

# 2. Docker 배포 실행
./deploy.sh

# 3. 서비스 확인
docker-compose ps
```

### 📊 배포 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx         │    │   FastAPI       │    │   PostgreSQL    │
│   (Frontend)    │───▶│   (Backend)     │───▶│   (Database)    │
│   Port: 80      │    │   Port: 4000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         │              ┌─────────────────┐
         └──────────────▶│     Ollama      │
                         │   (Local AI)    │
                         │   Port: 11434   │
                         └─────────────────┘
```

### 🔧 배포 명령어

```bash
# 기본 배포
./deploy.sh

# 완전 정리 후 재배포
./deploy.sh --clean --no-cache

# Ollama 포함 배포
./deploy.sh --setup-ollama

# 서비스 관리
docker-compose ps                    # 상태 확인
docker-compose logs -f              # 로그 확인
docker-compose restart backend      # 백엔드 재시작
docker-compose down                 # 서비스 중지
```

### 📋 배포 후 접속 URL

- **🌐 애플리케이션**: http://localhost
- **📄 백엔드 API**: http://localhost:4000
- **📚 API 문서**: http://localhost:4000/docs
- **🗄️ 데이터베이스**: localhost:5432
- **🦙 Ollama**: http://localhost:11434
- **🖥️ LM Studio**: http://localhost:1234

### 🔒 배포용 보안 설정

```env
# 프로덕션 보안 설정
ENVIRONMENT=production
DEBUG=false
ENABLE_EXTERNAL_AI=false
DEFAULT_AI_MODEL=local
POSTGRES_PASSWORD=your_secure_password
```

### 📖 상세 배포 가이드

더 자세한 배포 정보는 [DEPLOYMENT.md](./DEPLOYMENT.md)를 참조하세요:
- SSL/HTTPS 설정
- 모니터링 구성
- 백업 및 복원
- 문제 해결 가이드

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여하기

1. 이 저장소를 Fork합니다
2. 새로운 기능 브랜치를 생성합니다 (`git checkout -b feature/새기능`)
3. 변경사항을 커밋합니다 (`git commit -m '새 기능 추가'`)
4. 브랜치를 Push합니다 (`git push origin feature/새기능`)
5. Pull Request를 생성합니다

## 🧪 LM Studio 연결 테스트

LM Studio가 제대로 연결되는지 테스트하려면:

```bash
# LM Studio 연결 테스트 실행
python test_lmstudio.py
```

이 스크립트는 다음을 확인합니다:
- LM Studio 서버 연결 상태
- 사용 가능한 모델 목록
- 채팅 API 동작 여부
- JSON 형식 응답 파싱 가능 여부

**LM Studio 설정 방법:**
1. [LM Studio](https://lmstudio.ai) 다운로드 및 설치
2. 원하는 모델 다운로드 (예: Llama 2, Mistral 등)
3. "Local Server" 탭에서 서버 시작
4. 포트를 1234로 설정 (기본값)
5. 모델 로드 후 테스트 실행

## 📞 지원

문제가 발생하거나 질문이 있으시면:
- GitHub Issues에 등록해 주세요
- [macOS 문제 해결](#-macos-문제-해결) 섹션을 참고해 주세요
- [보안 권장사항](#-보안-권장사항)을 확인해 주세요
- API 문서를 확인해 주세요

## 🍎 macOS 전용 기능

- **자동 브라우저 열기**: 서버 시작 시 기본 브라우저 자동 실행
- **Homebrew 경로 자동 감지**: Apple Silicon/Intel Mac 자동 구분
- **성능 최적화**: Yarn 패키지 매니저 자동 감지 및 사용
- **macOS 통합**: 시스템 알림, Dock 아이콘 지원
- **보안 우선 설계**: 로컬 분석 기본값으로 데이터 보호
- **포트 충돌 방지**: 4000/4001 포트 사용으로 일반적인 충돌 회피

## 🌐 접속 URL

- **📱 메인 애플리케이션**: http://localhost:4001
- **📄 백엔드 API**: http://localhost:4000
- **📚 API 문서**: http://localhost:4000/docs
- **🔒 보안 상태**: http://localhost:4000/api/documents/security/status

---

**🎉🔒 macOS에서 안전하고 최적화된 Document Analyzer를 사용해 주셔서 감사합니다!** 
