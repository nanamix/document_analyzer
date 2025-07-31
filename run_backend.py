#!/usr/bin/env python3
"""
Document Analyzer Backend 실행 스크립트 (macOS 최적화)
"""
import os
import sys
import subprocess
import argparse
import platform
from pathlib import Path

def get_macos_info():
    """macOS 정보 확인"""
    if platform.system() == 'Darwin':
        # Apple Silicon vs Intel Mac 구분
        machine = platform.machine()
        if machine == 'arm64':
            return 'apple_silicon', '/opt/homebrew'
        else:
            return 'intel', '/usr/local'
    return None, None

def check_python_version():
    """Python 버전 확인"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 이상이 필요합니다.")
        print(f"현재 버전: {sys.version}")
        if platform.system() == 'Darwin':
            print("🍺 macOS에서 Python 업그레이드: brew install python")
        sys.exit(1)
    print(f"✅ Python 버전: {sys.version}")

def check_dependencies():
    """의존성 패키지 확인"""
    try:
        import fastapi
        import uvicorn
        print("✅ 주요 패키지가 설치되어 있습니다.")
    except ImportError as e:
        print(f"❌ 패키지가 설치되지 않았습니다: {e}")
        print("다음 명령어로 패키지를 설치하세요:")
        print("cd backend && source venv/bin/activate && pip install -r requirements.txt")
        if platform.system() == 'Darwin':
            print("🍎 macOS 사용자: ./install_dependencies.sh 실행을 권장합니다")
        sys.exit(1)

def check_env_file():
    """환경 파일 확인"""
    env_file = Path("backend/.env")
    env_example = Path("backend/.env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("⚠️  .env 파일이 없습니다.")
            create_env = input(".env.example을 복사하여 .env 파일을 생성하시겠습니까? (y/n): ")
            if create_env.lower() == 'y':
                import shutil
                shutil.copy(env_example, env_file)
                print("✅ .env 파일이 생성되었습니다.")
                
                # macOS에서 Tesseract 경로 자동 설정
                if platform.system() == 'Darwin':
                    arch, homebrew_prefix = get_macos_info()
                    tesseract_path = f"{homebrew_prefix}/bin/tesseract"
                    
                    # .env 파일에서 Tesseract 경로 업데이트
                    with open(env_file, 'r') as f:
                        content = f.read()
                    
                    if arch == 'apple_silicon':
                        content = content.replace(
                            'TESSERACT_CMD=/opt/homebrew/bin/tesseract',
                            f'TESSERACT_CMD={tesseract_path}'
                        )
                        print(f"🍎 Apple Silicon Mac 감지: Tesseract 경로를 {tesseract_path}로 설정")
                    else:
                        content = content.replace(
                            'TESSERACT_CMD=/opt/homebrew/bin/tesseract',
                            f'TESSERACT_CMD={tesseract_path}'
                        )
                        print(f"💻 Intel Mac 감지: Tesseract 경로를 {tesseract_path}로 설정")
                    
                    with open(env_file, 'w') as f:
                        f.write(content)
                
                print("⚠️  .env 파일에서 API 키를 설정해주세요!")
            else:
                print("❌ .env 파일이 필요합니다.")
                sys.exit(1)
        else:
            print("❌ .env.example 파일이 없습니다.")
            sys.exit(1)
    else:
        print("✅ .env 파일이 존재합니다.")

def check_tesseract():
    """Tesseract OCR 설치 확인"""
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, check=True)
        tesseract_path = subprocess.run(['which', 'tesseract'], 
                                      capture_output=True, text=True, check=True).stdout.strip()
        print("✅ Tesseract OCR가 설치되어 있습니다.")
        print(f"   버전: {result.stdout.split()[1]}")
        print(f"   경로: {tesseract_path}")
        
        # macOS에서 경로 확인 및 권장사항
        if platform.system() == 'Darwin':
            arch, expected_prefix = get_macos_info()
            if expected_prefix and not tesseract_path.startswith(expected_prefix):
                print(f"⚠️  Tesseract가 예상 경로({expected_prefix})에 설치되지 않았습니다.")
                print(f"   현재 경로: {tesseract_path}")
                
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Tesseract OCR가 설치되지 않았거나 PATH에 없습니다.")
        print("설치 방법:")
        if platform.system() == 'Darwin':
            print("  🍺 macOS (Homebrew): brew install tesseract tesseract-lang")
            arch, _ = get_macos_info()
            if arch:
                print(f"  💻 감지된 Mac: {arch}")
        else:
            print("  Ubuntu: sudo apt install tesseract-ocr tesseract-ocr-kor")
            print("  Windows: https://github.com/UB-Mannheim/tesseract/wiki")

def create_directories():
    """필요한 디렉토리 생성"""
    directories = ['backend/uploads', 'backend/logs']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ 디렉토리 생성: {directory}")

def run_server(host="0.0.0.0", port=4000, reload=True):
    """서버 실행 - 포트 4000으로 변경"""
    os.chdir("backend")
    
    # 가상환경 활성화 (Unix 계열)
    venv_activate = Path("venv/bin/activate")
    if venv_activate.exists() and platform.system() != 'Windows':
        print("🐍 가상환경을 활성화합니다...")
        # 가상환경의 Python 사용
        python_cmd = "venv/bin/python"
        uvicorn_cmd = "venv/bin/uvicorn"
        
        if not Path(uvicorn_cmd).exists():
            # 가상환경에 uvicorn이 없으면 pip로 설치된 것 사용
            uvicorn_cmd = "uvicorn"
    else:
        python_cmd = "python"
        uvicorn_cmd = "uvicorn"
    
    cmd = [
        uvicorn_cmd, 
        "app.main:app",
        "--host", host,
        "--port", str(port)
    ]
    
    if reload:
        cmd.append("--reload")
    
    print(f"🚀 서버를 시작합니다...")
    print(f"   URL: http://{host}:{port}")
    print(f"   API 문서: http://{host}:{port}/docs")
    print("   종료하려면 Ctrl+C를 누르세요.")
    
    if platform.system() == 'Darwin':
        print("🍎 macOS에서 실행 중...")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n✅ 서버가 정상적으로 종료되었습니다.")

def main():
    parser = argparse.ArgumentParser(description="Document Analyzer Backend 서버 (macOS 최적화)")
    parser.add_argument("--host", default="0.0.0.0", help="서버 호스트 (기본: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=4000, help="서버 포트 (기본: 4000)")
    parser.add_argument("--no-reload", action="store_true", help="자동 재시작 비활성화")
    parser.add_argument("--skip-checks", action="store_true", help="사전 검사 생략")
    
    args = parser.parse_args()
    
    print("📄 Document Analyzer Backend Server")
    if platform.system() == 'Darwin':
        arch, homebrew_prefix = get_macos_info()
        print(f"🍎 macOS {arch} 최적화 버전")
        print(f"🍺 Homebrew 경로: {homebrew_prefix}")
    print("=" * 50)
    
    if not args.skip_checks:
        print("🔍 사전 검사를 수행합니다...")
        check_python_version()
        check_dependencies()
        check_env_file()
        check_tesseract()
        create_directories()
        print("✅ 모든 검사가 완료되었습니다.")
        print("-" * 50)
    
    run_server(
        host=args.host,
        port=args.port,
        reload=not args.no_reload
    )

if __name__ == "__main__":
    main() 