-- Document Analyzer 데이터베이스 초기화 스크립트

-- 확장 기능 활성화
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 한국어 검색을 위한 텍스트 검색 설정
CREATE TEXT SEARCH CONFIGURATION korean (COPY = simple);

-- 인덱스 최적화를 위한 설정
SET maintenance_work_mem = '256MB';

-- 문서 테이블 생성 (SQLAlchemy가 자동으로 생성하지만, 인덱스 추가)
-- SQLAlchemy가 테이블을 생성한 후 실행될 수 있도록 조건부 생성

-- 성능 향상을 위한 인덱스 (테이블이 생성된 후 적용)
DO $$
BEGIN
    -- documents 테이블이 존재하는지 확인 후 인덱스 생성
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'documents') THEN
        -- 파일명 검색 최적화
        CREATE INDEX IF NOT EXISTS idx_documents_filename 
        ON documents USING gin(filename gin_trgm_ops);
        
        -- 업로드 날짜 정렬 최적화
        CREATE INDEX IF NOT EXISTS idx_documents_upload_date 
        ON documents (upload_date DESC);
        
        -- 파일 타입별 검색 최적화
        CREATE INDEX IF NOT EXISTS idx_documents_file_type 
        ON documents (file_type);
        
        -- 텍스트 검색 최적화
        CREATE INDEX IF NOT EXISTS idx_documents_extracted_text 
        ON documents USING gin(to_tsvector('korean', extracted_text));
    END IF;
END $$;

-- 분석 결과 테이블이 생성된 후 인덱스 추가
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'analysis_results') THEN
        -- 분석 날짜 정렬 최적화
        CREATE INDEX IF NOT EXISTS idx_analysis_results_analysis_date 
        ON analysis_results (analysis_date DESC);
        
        -- AI 모델별 검색 최적화
        CREATE INDEX IF NOT EXISTS idx_analysis_results_ai_model 
        ON analysis_results (ai_model);
        
        -- 사용자 의도별 검색 최적화
        CREATE INDEX IF NOT EXISTS idx_analysis_results_user_intent 
        ON analysis_results USING gin(user_intent gin_trgm_ops);
    END IF;
END $$;

-- 성능 최적화 설정
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- 설정 적용
SELECT pg_reload_conf();

-- 초기 통계 정보 수집
ANALYZE;

-- 초기화 완료 로그
DO $$
BEGIN
    RAISE NOTICE 'Document Analyzer 데이터베이스 초기화 완료';
    RAISE NOTICE '확장 기능: uuid-ossp, pg_trgm 활성화됨';
    RAISE NOTICE '텍스트 검색: korean 설정 생성됨';
    RAISE NOTICE '성능 최적화: 인덱스 및 설정 적용됨';
END $$; 