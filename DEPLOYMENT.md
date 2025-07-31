# 🚀 Document Analyzer - 배포 가이드

## 📋 개요

이 가이드는 Document Analyzer 애플리케이션을 Docker와 PostgreSQL을 사용하여 실제 서버에 배포하는 방법을 설명합니다.

## 🏗️ 아키텍처

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

## 🛠️ 사전 요구사항

### 필수 설치 항목

1. **Docker** (v20.10+)
   ```bash
   # macOS (Homebrew)
   brew install docker

   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install docker.io docker-compose

   # CentOS/RHEL
   sudo yum install docker docker-compose
   ```

2. **Docker Compose** (v2.0+)
   ```bash
   # 최신 버전 설치 확인
   docker-compose --version
   ```

### 시스템 요구사항

- **메모리**: 최소 4GB, 권장 8GB+
- **저장공간**: 최소 10GB, 권장 50GB+
- **CPU**: 최소 2 코어, 권장 4 코어+

## 🚀 빠른 배포

### 1️⃣ 프로젝트 복제

```bash
git clone <repository-url>
cd document_analyzer
```

### 2️⃣ 환경 설정

```bash
# 배포용 환경 변수 복사 및 수정
cp .env.production .env.production.local

# 중요: 데이터베이스 비밀번호 변경
nano .env.production.local
```

**필수 수정 항목:**
```env
# 강력한 데이터베이스 비밀번호로 변경
POSTGRES_PASSWORD=your_very_secure_password_here

# 도메인 설정 (실제 도메인으로 변경)
CORS_ORIGINS=https://yourdomain.com
ALLOWED_HOSTS=yourdomain.com
```

### 3️⃣ 배포 실행

```bash
# 기본 배포
./deploy.sh

# 완전 정리 후 배포
./deploy.sh --clean --no-cache

# Ollama 모델 포함 배포
./deploy.sh --setup-ollama
```

## 📊 서비스 구성

### 🗄️ 데이터베이스 (PostgreSQL)

- **이미지**: `postgres:15-alpine`
- **포트**: `5432`
- **볼륨**: `postgres_data`
- **기능**: 
  - 자동 백업
  - 성능 최적화
  - 한국어 검색 지원

### 🔧 백엔드 (FastAPI)

- **빌드**: `./backend/Dockerfile`
- **포트**: `4000`
- **기능**:
  - RESTful API
  - AI 분석 엔진
  - OCR 처리
  - 파일 업로드

### 🌐 프론트엔드 (React + Nginx)

- **빌드**: `./frontend/Dockerfile`
- **포트**: `80` (HTTP), `443` (HTTPS)
- **기능**:
  - SPA 서빙
  - API 프록시
  - 정적 파일 캐싱
  - 보안 헤더

### 🦙 Ollama (로컬 AI)

- **이미지**: `ollama/ollama:latest`
- **포트**: `11434`
- **기능**:
  - 로컬 LLM 실행
  - GPU 지원 (선택)
  - 모델 관리

## 🔧 고급 설정

### SSL/HTTPS 설정

1. **Let's Encrypt 인증서 획득**:
   ```bash
   # Certbot 설치
   sudo apt-get install certbot

   # 인증서 발급
   sudo certbot certonly --standalone -d yourdomain.com
   ```

2. **Nginx 설정 수정**:
   ```nginx
   # frontend/nginx.conf에 SSL 설정 추가
   server {
       listen 443 ssl;
       ssl_certificate /etc/ssl/certs/yourdomain.com.pem;
       ssl_certificate_key /etc/ssl/private/yourdomain.com.key;
       # ... 나머지 설정
   }
   ```

### 환경별 설정

#### 🔧 개발 환경
```bash
# 개발 모드로 실행 (SQLite 사용)
docker-compose -f docker-compose.dev.yml up -d
```

#### 🚀 스테이징 환경
```bash
# 스테이징 환경 변수 사용
docker-compose --env-file .env.staging up -d
```

#### 🏭 프로덕션 환경
```bash
# 프로덕션 환경 (기본)
docker-compose --env-file .env.production up -d
```

### 모니터링 설정

#### 1. Prometheus + Grafana
```yaml
# docker-compose.monitoring.yml 추가
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
      
  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
```

#### 2. 로그 수집
```bash
# 로그 확인
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

## 🔐 보안 설정

### 1. 방화벽 설정

```bash
# UFW 설정 (Ubuntu)
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### 2. 데이터베이스 보안

- 강력한 비밀번호 사용
- 외부 접근 차단
- 정기적인 백업

### 3. AI 보안 설정

```env
# 기본: 로컬 분석만 사용
ENABLE_EXTERNAL_AI=false
DEFAULT_AI_MODEL=local

# 외부 AI 사용 시 동의 필수
REQUIRE_EXPLICIT_CONSENT=true
ENABLE_DATA_MASKING=true
```

## 📈 성능 최적화

### 1. 데이터베이스 튜닝

```sql
-- PostgreSQL 설정 최적화
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
SELECT pg_reload_conf();
```

### 2. Nginx 캐싱

```nginx
# 정적 파일 캐싱
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, no-transform";
}
```

### 3. 컨테이너 리소스 제한

```yaml
# docker-compose.yml에 리소스 제한 추가
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
```

## 🔄 운영 및 유지보수

### 일상적인 관리

```bash
# 서비스 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f --tail=100

# 서비스 재시작
docker-compose restart backend

# 설정 다시 로드
docker-compose up -d --force-recreate
```

### 백업 및 복원

```bash
# 데이터베이스 백업
docker exec document_analyzer_db pg_dump -U postgres document_analyzer > backup.sql

# 파일 업로드 백업
docker cp document_analyzer_backend:/app/uploads ./uploads_backup

# 복원
docker exec -i document_analyzer_db psql -U postgres document_analyzer < backup.sql
```

### 업데이트

```bash
# 코드 업데이트
git pull origin main

# 이미지 재빌드 및 배포
./deploy.sh --no-cache

# 특정 서비스만 업데이트
docker-compose up -d --build backend
```

## 🚨 문제 해결

### 자주 발생하는 문제

#### 1. 포트 충돌
```bash
# 포트 사용 확인
sudo lsof -i :80
sudo lsof -i :4000

# 충돌 프로세스 종료
sudo kill -9 <PID>
```

#### 2. 메모리 부족
```bash
# 메모리 사용량 확인
docker stats

# 불필요한 컨테이너/이미지 정리
docker system prune -a
```

#### 3. 데이터베이스 연결 실패
```bash
# 데이터베이스 로그 확인
docker-compose logs db

# 연결 테스트
docker exec document_analyzer_db pg_isready -U postgres
```

### 로그 위치

- **애플리케이션 로그**: `./logs/`
- **Docker 로그**: `docker-compose logs`
- **Nginx 로그**: 컨테이너 내 `/var/log/nginx/`

## 📞 지원

문제가 발생하거나 질문이 있으시면:

1. **문서 확인**: 이 가이드와 `README.md`
2. **로그 확인**: `docker-compose logs`
3. **이슈 리포트**: GitHub Issues
4. **커뮤니티**: 개발자 포럼

---

**⚠️ 중요**: 프로덕션 배포 시 반드시 보안 설정을 검토하고, 정기적인 백업을 수행하세요. 