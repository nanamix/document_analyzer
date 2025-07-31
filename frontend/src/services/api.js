import axios from 'axios';

// API 기본 설정 - 포트 4000으로 변경 (충돌 방지)
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:4000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터
api.interceptors.request.use(
  (config) => {
    console.log('API 요청:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('API 요청 오류:', error);
    return Promise.reject(error);
  }
);

// 응답 인터셉터
api.interceptors.response.use(
  (response) => {
    console.log('API 응답:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('API 응답 오류:', error.response?.status, error.message);
    return Promise.reject(error);
  }
);

// API 서비스 함수들
export const documentService = {
  // 문서 업로드
  uploadDocuments: async (files, userIntent = '') => {
    const formData = new FormData();
    
    // 파일들 추가
    files.forEach(file => {
      formData.append('files', file);
    });
    
    // 사용자 의도 추가
    if (userIntent) {
      formData.append('user_intent', userIntent);
    }
    
    const response = await api.post('/api/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  // 문서 목록 조회
  getDocuments: async (skip = 0, limit = 100) => {
    const response = await api.get('/api/documents/', {
      params: { skip, limit }
    });
    return response.data;
  },

  // 특정 문서 조회
  getDocument: async (documentId) => {
    const response = await api.get(`/api/documents/${documentId}`);
    return response.data;
  },

  // 🔒 보안 강화된 문서 분석
  analyzeDocuments: async (
    documentIds, 
    userIntent, 
    aiModel = 'local', 
    additionalContext = '', 
    userConsent = false
  ) => {
    // 외부 AI 사용 시 보안 경고
    const externalAIModels = ['openai', 'claude', 'deepseek'];
    if (externalAIModels.includes(aiModel)) {
      if (!userConsent) {
        throw new Error('외부 AI 사용을 위해 명시적 동의가 필요합니다.');
      }
      console.warn(`🔒 보안 경고: ${aiModel.toUpperCase()} 사용 - 데이터가 외부 서버로 전송됩니다.`);
    } else {
      console.info(`✅ 안전한 로컬 분석: ${aiModel}`);
    }

    const response = await api.post('/api/documents/analyze', {
      document_ids: documentIds,
      user_intent: userIntent,
      ai_model: aiModel,
      additional_context: additionalContext,
      user_consent: userConsent
    });
    return response.data;
  },

  // 문서 삭제
  deleteDocument: async (documentId) => {
    const response = await api.delete(`/api/documents/${documentId}`);
    return response.data;
  },

  // 문서 분석 결과 조회
  getDocumentAnalysis: async (documentId) => {
    const response = await api.get(`/api/documents/${documentId}/analysis`);
    return response.data;
  },

  // 🔒 보안 상태 확인
  getSecurityStatus: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

// 헬스 체크
export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

// 에러 핸들링 유틸리티
export const handleApiError = (error) => {
  if (error.response) {
    // 서버가 응답했지만 오류 상태 코드
    const { status, data } = error.response;
    
    // 보안 관련 오류 특별 처리
    if (status === 403 && data.detail?.includes('동의')) {
      return {
        message: '🔒 보안 경고: 외부 AI 사용을 위해 명시적 동의가 필요합니다.',
        status,
        type: 'security_error'
      };
    }
    
    return {
      message: data.detail || `서버 오류 (${status})`,
      status,
      type: 'server_error'
    };
  } else if (error.request) {
    // 요청이 만들어졌지만 응답을 받지 못함
    return {
      message: '서버에 연결할 수 없습니다. 네트워크를 확인해주세요.',
      type: 'network_error'
    };
  } else {
    // 요청 설정 중 오류
    return {
      message: error.message || '요청 처리 중 오류가 발생했습니다.',
      type: 'request_error'
    };
  }
};

export default api; 