#!/bin/bash

# ============================================================================
# Document Analyzer - Docker 배포 스크립트
# ============================================================================

set -e  # 에러 발생 시 스크립트 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 배너 출력
print_banner() {
    echo -e "${BLUE}"
    echo "============================================================"
    echo "🚀 Document Analyzer - Docker 배포 스크립트"
    echo "============================================================"
    echo -e "${NC}"
}

# Docker 및 Docker Compose 확인
check_prerequisites() {
    log_info "사전 요구사항 확인 중..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker가 설치되지 않았습니다."
        echo "Docker 설치: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose가 설치되지 않았습니다."
        echo "Docker Compose 설치: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    log_success "Docker 및 Docker Compose 확인 완료"
}

# 환경 설정 확인
check_environment() {
    log_info "환경 설정 확인 중..."
    
    if [ ! -f ".env.production" ]; then
        log_warning ".env.production 파일이 없습니다."
        log_info "기본 설정으로 .env.production 파일을 생성합니다..."
        cp .env.production.example .env.production 2>/dev/null || {
            log_error ".env.production.example 파일도 없습니다."
            log_info "수동으로 .env.production 파일을 생성하고 설정을 확인해주세요."
            exit 1
        }
    fi
    
    log_success "환경 설정 확인 완료"
}

# 이전 컨테이너 정리
cleanup_containers() {
    log_info "이전 컨테이너 정리 중..."
    
    # 실행 중인 컨테이너 확인 및 중지
    if docker-compose ps -q | grep -q .; then
        log_warning "실행 중인 컨테이너를 중지합니다..."
        docker-compose down
    fi
    
    # 사용하지 않는 이미지 정리
    if [ "$1" = "--clean" ]; then
        log_info "사용하지 않는 이미지 정리 중..."
        docker system prune -f
        docker image prune -f
    fi
    
    log_success "컨테이너 정리 완료"
}

# 이미지 빌드
build_images() {
    log_info "Docker 이미지 빌드 중..."
    
    # 빌드 로그를 위한 디렉토리 생성
    mkdir -p logs
    
    # 캐시 사용하지 않고 빌드 (--no-cache 옵션)
    if [ "$1" = "--no-cache" ]; then
        log_info "캐시 없이 이미지 빌드 중..."
        docker-compose build --no-cache 2>&1 | tee logs/build.log
    else
        docker-compose build 2>&1 | tee logs/build.log
    fi
    
    log_success "Docker 이미지 빌드 완료"
}

# 서비스 시작
start_services() {
    log_info "서비스 시작 중..."
    
    # 백그라운드에서 서비스 시작
    docker-compose --env-file .env.production up -d
    
    log_success "서비스 시작 완료"
}

# 헬스체크
health_check() {
    log_info "서비스 헬스체크 중..."
    
    # 최대 대기 시간 (초)
    MAX_WAIT=120
    WAIT_TIME=0
    
    while [ $WAIT_TIME -lt $MAX_WAIT ]; do
        # 백엔드 헬스체크
        if curl -s http://localhost:4000/health > /dev/null 2>&1; then
            log_success "백엔드 서비스 정상 동작 중"
            break
        fi
        
        echo -n "."
        sleep 5
        WAIT_TIME=$((WAIT_TIME + 5))
    done
    
    if [ $WAIT_TIME -ge $MAX_WAIT ]; then
        log_error "서비스 시작 시간 초과"
        log_info "로그를 확인하세요: docker-compose logs"
        exit 1
    fi
    
    # 프론트엔드 헬스체크
    if curl -s http://localhost/ > /dev/null 2>&1; then
        log_success "프론트엔드 서비스 정상 동작 중"
    else
        log_warning "프론트엔드 서비스 확인 필요"
    fi
}

# 서비스 상태 출력
show_status() {
    log_info "서비스 상태:"
    docker-compose ps
    
    echo ""
    log_info "접속 URL:"
    echo "🌐 애플리케이션: http://localhost"
    echo "📄 백엔드 API: http://localhost:4000"
    echo "📚 API 문서: http://localhost:4000/docs"
    echo "🔒 보안 상태: http://localhost:4000/api/documents/security/status"
    echo "🗄️  데이터베이스: localhost:5432"
    echo "🦙 Ollama (로컬 AI): http://localhost:11434"
}

# Ollama 모델 다운로드
setup_ollama() {
    log_info "Ollama 모델 설정 중..."
    
    # Ollama 컨테이너가 준비될 때까지 대기
    sleep 30
    
    # 기본 모델 다운로드
    docker exec document_analyzer_ollama ollama pull llama2 || {
        log_warning "Ollama 모델 다운로드 실패 (선택적 기능)"
    }
    
    log_success "Ollama 설정 완료"
}

# 메인 배포 함수
deploy() {
    print_banner
    
    # 옵션 파싱
    CLEAN_FLAG=""
    CACHE_FLAG=""
    SETUP_OLLAMA=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --clean)
                CLEAN_FLAG="--clean"
                shift
                ;;
            --no-cache)
                CACHE_FLAG="--no-cache"
                shift
                ;;
            --setup-ollama)
                SETUP_OLLAMA=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "알 수 없는 옵션: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 배포 과정 실행
    check_prerequisites
    check_environment
    cleanup_containers $CLEAN_FLAG
    build_images $CACHE_FLAG
    start_services
    health_check
    
    # Ollama 설정 (옵션)
    if [ "$SETUP_OLLAMA" = true ]; then
        setup_ollama
    fi
    
    show_status
    
    log_success "🎉 Document Analyzer 배포 완료!"
    echo ""
    log_info "📋 유용한 명령어:"
    echo "  - 로그 확인: docker-compose logs -f"
    echo "  - 서비스 중지: docker-compose down"
    echo "  - 서비스 재시작: docker-compose restart"
    echo "  - 볼륨 포함 완전 삭제: docker-compose down -v"
}

# 도움말
show_help() {
    echo "사용법: $0 [옵션]"
    echo ""
    echo "옵션:"
    echo "  --clean         이전 이미지 및 컨테이너 완전 정리"
    echo "  --no-cache      캐시 없이 이미지 빌드"
    echo "  --setup-ollama  Ollama 모델 자동 다운로드"
    echo "  --help          이 도움말 출력"
    echo ""
    echo "예시:"
    echo "  $0                      # 기본 배포"
    echo "  $0 --clean --no-cache   # 완전 정리 후 캐시 없이 빌드"
    echo "  $0 --setup-ollama       # Ollama 모델 포함 배포"
}

# 스크립트 실행
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    deploy "$@"
fi 