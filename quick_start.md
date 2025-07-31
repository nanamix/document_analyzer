# 🚀 Document Analyzer 빠른 시작 가이드 (macOS 최적화) 🔒 보안 우선

**🍎 macOS 사용자를 위한 3분 완성 가이드!**
**🔒 보안 우선: 기본적으로 모든 분석이 로컬에서 수행됩니다!**

## 📋 사전 체크리스트

시작하기 전에 다음 항목들을 확인해주세요:

- [ ] **macOS 10.15** (Catalina) 이상
- [ ] **Homebrew** 설치됨 ([brew.sh](https://brew.sh))
- [ ] ✅ **AI API 키 불필요** (로컬 분석 기본값)

## 🎯 3분 완성 실행법 (100% 로컬)

```bash
# 1️⃣ 의존성 자동 설치 (Apple Silicon/Intel 자동 감지)
./install_dependencies.sh

# 2️⃣ 환경 설정 (보안 우선 - API 키 불필요)
cp backend/.env.example backend/.env
# 기본값으로 로컬 분석만 활성화됨!

# 3️⃣ 한 번에 실행 (브라우저 자동 열림)
./run.sh
```

**🎉🔒 완료! 브라우저에서 http://localhost:4001 이 자동으로 열리며, 모든 분석이 로컬에서 안전하게 수행됩니다.**

## 🛡️ 보안 우선 특징

### ✅ 기본 보안 수준
- **🟢 로컬 분석**: 문서 내용이 외부로 전송되지 않음
- **🔒 데이터 보호**: 민감한 정보 자동 마스킹
- **🚫 외부 AI 비활성화**: 기본값으로 외부 AI 사용 금지
- **⚡ 즉시 사용 가능**: API 키 없이도 완전 동작

### 🍎 macOS 최적화 특징

#### ✨ 자동 감지 기능
- **Apple Silicon (M1/M2/M3)**: `/opt/homebrew` 경로 자동 설정
- **Intel Mac**: `/usr/local` 경로 자동 설정
- **Tesseract OCR**: 설치 위치 자동 감지 및 설정

#### 🚀 성능 최적화
- **Yarn** 패키지 매니저 자동 감지 (npm보다 빠름)
- **가상환경** 자동 생성 및 활성화
- **포트 충돌** 자동 감지 및 안내 (4000/4001 사용)

## 📝 단계별 상세 설명

### 1단계: Homebrew 설치 (필요시)
```bash
# Homebrew가 없는 경우에만 실행
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2단계: 프로젝트 의존성 설치
```bash
./install_dependencies.sh
```

**이 스크립트가 자동으로 수행하는 작업:**
- macOS 아키텍처 감지 (Apple Silicon vs Intel)
- Python, Node.js, Tesseract 설치 확인
- 백엔드 가상환경 생성
- 프론트엔드 패키지 설치 (Yarn 우선 사용)
- Tesseract 경로 자동 설정
- **보안 우선 설정 적용**

### 3단계: 환경 설정 (보안 우선)
```bash
cp backend/.env.example backend/.env
```

**기본값으로 로컬 분석만 활성화:**

```env
# 🔒 보안 설정 (데이터 보호 우선)
ENABLE_EXTERNAL_AI=false  # 외부 AI 비활성화
DEFAULT_AI_MODEL=local    # 로컬 분석 기본값
ENABLE_DATA_MASKING=true  # 민감 정보 마스킹

# Server Settings - 충돌 방지 포트
PORT=4000                 # 백엔드 포트
FRONTEND_PORT=4001        # 프론트엔드 포트

# ✅ API 키 불필요 - 로컬 분석으로 완전 동작!
```

### 4단계: 애플리케이션 실행

**🎯 추천: 한 번에 실행**
```bash
./run.sh
```

**또는 개별 실행:**
```bash
# 터미널 1: 백엔드 (포트 4000)
python run_backend.py

# 터미널 2: 프론트엔드 (포트 4001)
./run_frontend.sh
```

## 🌐 접속 확인

실행이 완료되면 자동으로 브라우저가 열리며:

- **📱 메인 앱**: http://localhost:4001 (자동 열림)
- **🔗 백엔드 API**: http://localhost:4000  
- **📚 API 문서**: http://localhost:4000/docs
- **🔒 보안 상태**: http://localhost:4000/api/documents/security/status

## 🧪 첫 번째 테스트 (100% 안전)

1. **📄 http://localhost:4001** 접속
2. **📤 파일 업로드** - PDF/이미지 드래그앤드롭
3. **🎯 목적 선택** - "면접 준비" 선택
4. **🛡️ AI 모델** - "🔒 로컬 분석" 선택 (기본값)
5. **▶️ 분석 시작** 클릭!

**✅ 결과**: 문서 내용이 외부로 전송되지 않고 로컬에서 분석 완료!

## 🔒 선택적 보안 설정

### 🟢 최고 보안 (기본값)
```env
ENABLE_EXTERNAL_AI=false
DEFAULT_AI_MODEL=local
PORT=4000
FRONTEND_PORT=4001
```
- ✅ **완전 로컬 처리**
- ✅ **API 키 불필요**
- ✅ **즉시 사용 가능**

### 🟡 중간 보안 (로컬 AI)
```bash
# Ollama 설치 (선택사항)
brew install ollama
ollama serve
ollama pull llama2

# .env 설정
DEFAULT_AI_MODEL=ollama
```
- ✅ **로컬 AI 모델 사용**
- ✅ **더 고급 분석**
- ✅ **여전히 안전**

### 🔴 주의 (외부 AI - 고급 사용자)
```env
ENABLE_EXTERNAL_AI=true
REQUIRE_EXPLICIT_CONSENT=true  # 동의 필수
ENABLE_DATA_MASKING=true       # 마스킹 활성화
```
- ⚠️ **사용자 동의 필요**
- ⚠️ **API 키 필요**
- ⚠️ **데이터 마스킹 적용**

## 🔑 외부 AI 사용 (선택사항)

**⚠️ 주의: 외부 AI 사용 시 문서 내용이 외부 서버로 전송됩니다**

### OpenAI (고성능)
1. 🌐 https://platform.openai.com 접속
2. 🔑 **API Keys** → **Create new secret key**
3. 📋 키를 복사하여 `.env`에 추가
4. ⚙️ `ENABLE_EXTERNAL_AI=true` 설정

### Anthropic Claude (창의적)
1. 🌐 https://console.anthropic.com 접속
2. 🔑 **API Keys** → **Create Key**  
3. 📋 키를 복사하여 `.env`에 추가

### DeepSeek (비용 효율적)
1. 🌐 https://platform.deepseek.com 접속
2. 🔑 **API Keys** → **New API Key**
3. 📋 키를 복사하여 `.env`에 추가

## ❗ macOS 문제 해결

### 🔧 자주 발생하는 오류

**1. Tesseract 경로 오류**
```bash
# 자동 수정 (Apple Silicon)
export TESSERACT_CMD=/opt/homebrew/bin/tesseract

# 자동 수정 (Intel Mac)  
export TESSERACT_CMD=/usr/local/bin/tesseract
```

**2. 포트 이미 사용 중**
```bash
# 사용 중인 프로세스 확인
lsof -ti:4000  # 백엔드
lsof -ti:4001  # 프론트엔드

# 다른 포트로 실행
python run_backend.py --port 4002
```

**3. Python/Node.js 없음**
```bash
# Homebrew로 한 번에 설치
brew install python node tesseract tesseract-lang
```

**4. 권한 오류**
```bash
# Xcode Command Line Tools 설치
xcode-select --install

# 스크립트 실행 권한 확인
chmod +x *.sh *.py
```

### 🚀 성능 향상 팁

**Yarn 사용 (npm보다 빠름):**
```bash
brew install yarn
cd frontend && yarn install
```

**iTerm2 + Oh My Zsh:**
```bash
brew install --cask iterm2
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

## 🎉 성공 확인

다음이 모두 표시되면 성공입니다:

```
✅ Python 버전: 3.x.x
✅ Node.js 버전: v18.x.x  
✅ Tesseract OCR가 설치되어 있습니다
🔒 외부 AI 비활성화 - 로컬 분석만 사용
✅ 백엔드 서버 실행 중 (http://localhost:4000)
✅ 프론트엔드 서버 실행 중 (http://localhost:4001)
🍎 macOS에서 실행 중...
💡 브라우저가 자동으로 열립니다.
🛡️ 보안 우선 모드 활성화
```

## 🛡️ 보안 권장사항

### ✅ 권장 사용법
- **로컬 분석 우선 사용** (기본값)
- **기업 기밀 문서**: 외부 AI 절대 사용 금지
- **개인 문서**: 로컬 분석으로 충분
- **민감 정보 포함**: 로컬 분석만 사용

### ⚠️ 외부 AI 사용 시
- **반드시 사용자 동의** 확인
- **민감한 정보** 사전 제거 권장
- **기업 정책** 확인 필수

## 🌐 주요 URL

- **📱 메인 애플리케이션**: http://localhost:4001
- **📄 백엔드 API**: http://localhost:4000
- **📚 API 문서**: http://localhost:4000/docs
- **🔒 보안 상태**: http://localhost:4000/api/documents/security/status

**🎊🔒 축하합니다! Document Analyzer가 macOS에서 안전하고 완벽하게 실행되고 있습니다!**

---

더 자세한 정보는 [README.md](README.md)를 참고하세요. 