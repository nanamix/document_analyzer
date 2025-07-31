#!/usr/bin/env python3
"""
데이터베이스 마이그레이션: user_document_type 컬럼 추가
"""
import sqlite3
import os
import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import settings

def migrate_add_user_document_type():
    """user_document_type 컬럼 추가 마이그레이션"""
    try:
        # SQLite 데이터베이스 파일 경로
        db_path = settings.DATABASE_URL.replace('sqlite:///', '')
        if not os.path.exists(db_path):
            print(f"❌ 데이터베이스 파일을 찾을 수 없습니다: {db_path}")
            return False
        
        print(f"🔧 마이그레이션 시작: {db_path}")
        
        # SQLite 연결
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 기존 컬럼 확인
        cursor.execute("PRAGMA table_info(documents)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"📋 현재 컬럼: {columns}")
        
        # user_document_type 컬럼이 이미 있는지 확인
        if 'user_document_type' in columns:
            print("✅ user_document_type 컬럼이 이미 존재합니다")
            return True
        
        # 컬럼 추가
        print("➕ user_document_type 컬럼 추가 중...")
        cursor.execute("ALTER TABLE documents ADD COLUMN user_document_type TEXT")
        
        # 변경사항 커밋
        conn.commit()
        
        # 변경사항 확인
        cursor.execute("PRAGMA table_info(documents)")
        new_columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 업데이트된 컬럼: {new_columns}")
        
        if 'user_document_type' in new_columns:
            print("✅ 마이그레이션 성공!")
            return True
        else:
            print("❌ 마이그레이션 실패")
            return False
            
    except Exception as e:
        print(f"❌ 마이그레이션 중 오류: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔄 user_document_type 컬럼 추가 마이그레이션")
    print("=" * 50)
    
    success = migrate_add_user_document_type()
    
    if success:
        print("\n✅ 마이그레이션 완료!")
        print("이제 서버를 재시작하세요.")
    else:
        print("\n❌ 마이그레이션 실패!")
        print("데이터베이스 파일을 확인하고 다시 시도하세요.") 