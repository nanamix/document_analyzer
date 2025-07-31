import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { 
  Upload, 
  Button, 
  Select, 
  Input, 
  Card, 
  List, 
  Typography, 
  message, 
  Progress,
  Space,
  Tag
} from 'antd';
import { 
  InboxOutlined, 
  FileTextOutlined, 
  DeleteOutlined,
  CloudUploadOutlined 
} from '@ant-design/icons';
import { useMutation, useQueryClient } from 'react-query';
import { documentService, handleApiError } from '../services/api';

const { Dragger } = Upload;
const { Option } = Select;
const { TextArea } = Input;
const { Title, Text } = Typography;

const DocumentUpload = () => {
  const [files, setFiles] = useState([]);
  const [userIntent, setUserIntent] = useState('면접 준비');
  const [additionalContext, setAdditionalContext] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [documentTypes, setDocumentTypes] = useState({}); // 문서 유형 상태
  
  const queryClient = useQueryClient();

  // 파일 업로드 뮤테이션
  const uploadMutation = useMutation(
    ({ files, userIntent, documentTypes }) => documentService.uploadDocuments(files, userIntent, documentTypes),
    {
      onSuccess: (data) => {
        message.success(`${data.length}개 문서가 성공적으로 업로드되었습니다!`);
        setFiles([]);
        setUploadProgress(0);
        setDocumentTypes({});
        queryClient.invalidateQueries('documents');
      },
      onError: (error) => {
        const errorInfo = handleApiError(error);
        message.error(errorInfo.message);
        setUploadProgress(0);
      },
    }
  );

  // 드래그 앤 드롭 설정
  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    // 거부된 파일들 처리
    if (rejectedFiles.length > 0) {
      rejectedFiles.forEach(({ file, errors }) => {
        errors.forEach(error => {
          if (error.code === 'file-too-large') {
            message.error(`${file.name}: 파일 크기가 너무 큽니다 (최대 50MB)`);
          } else if (error.code === 'file-invalid-type') {
            message.error(`${file.name}: 지원하지 않는 파일 형식입니다`);
          } else {
            message.error(`${file.name}: ${error.message}`);
          }
        });
      });
    }

    // 허용된 파일들 추가
    if (acceptedFiles.length > 0) {
      setFiles(prev => [...prev, ...acceptedFiles]);
      message.success(`${acceptedFiles.length}개 파일이 추가되었습니다`);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg']
    },
    maxSize: 50 * 1024 * 1024, // 50MB
  });

  // 파일 제거
  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
    // 문서 유형도 함께 제거
    setDocumentTypes(prev => {
      const newTypes = { ...prev };
      delete newTypes[index];
      return newTypes;
    });
  };

  // 업로드 실행
  const handleUpload = async () => {
    if (files.length === 0) {
      message.warning('업로드할 파일을 선택해주세요');
      return;
    }

    if (!userIntent.trim()) {
      message.warning('사용자 의도를 입력해주세요');
      return;
    }

    setUploadProgress(10);
    
    try {
      await uploadMutation.mutateAsync({ 
        files, 
        userIntent: userIntent.trim(),
        documentTypes
      });
    } catch (error) {
      console.error('Upload error:', error);
    }
  };

  // 파일 크기 포매팅
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // 파일 타입 아이콘
  const getFileTypeTag = (file) => {
    const extension = file.name.split('.').pop().toLowerCase();
    if (extension === 'pdf') {
      return <Tag color="red">PDF</Tag>;
    } else if (['png', 'jpg', 'jpeg'].includes(extension)) {
      return <Tag color="blue">이미지</Tag>;
    }
    return <Tag>{extension.toUpperCase()}</Tag>;
  };

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <Card>
        <Title level={4}>📤 문서 업로드</Title>
        
        {/* 드래그 앤 드롭 영역 */}
        <div
          {...getRootProps()}
          style={{
            border: `2px dashed ${isDragActive ? '#1890ff' : '#d9d9d9'}`,
            borderRadius: '8px',
            padding: '40px 20px',
            textAlign: 'center',
            backgroundColor: isDragActive ? '#f0f2ff' : '#fafafa',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            marginBottom: '20px'
          }}
        >
          <input {...getInputProps()} />
          <InboxOutlined style={{ fontSize: '48px', color: '#1890ff', marginBottom: '16px' }} />
          <Title level={4} style={{ margin: '0 0 8px 0' }}>
            {isDragActive ? '파일을 여기에 놓으세요' : '파일을 드래그하거나 클릭하여 업로드'}
          </Title>
          <Text type="secondary">
            PDF, PNG, JPG 파일 지원 (최대 50MB)
          </Text>
        </div>

        {/* 선택된 파일 목록 */}
        {files.length > 0 && (
          <Card size="small" style={{ marginBottom: '20px' }}>
            <Title level={5}>선택된 파일 ({files.length}개)</Title>
            <List
              dataSource={files}
              renderItem={(file, index) => (
                <List.Item
                  actions={[
                    <Button
                      type="text"
                      icon={<DeleteOutlined />}
                      onClick={() => removeFile(index)}
                      danger
                    />
                  ]}
                >
                  <List.Item.Meta
                    avatar={<FileTextOutlined style={{ fontSize: '16px' }} />}
                    title={
                      <Space>
                        {file.name}
                        {getFileTypeTag(file)}
                      </Space>
                    }
                    description={
                      <Space direction="vertical" size="small" style={{ width: '100%' }}>
                        <Text type="secondary">{formatFileSize(file.size)}</Text>
                        {/* 면접 준비일 때만 문서 유형 선택 표시 */}
                        {userIntent === '면접 준비' && (
                          <div>
                            <Text strong style={{ fontSize: '12px' }}>문서 유형:</Text>
                            <Select
                              size="small"
                              style={{ width: 150, marginLeft: 8 }}
                              placeholder="문서 유형 선택"
                              value={documentTypes[index] || ''}
                              onChange={(value) => setDocumentTypes(prev => ({ ...prev, [index]: value }))}
                            >
                              <Option value="이력서">📄 이력서</Option>
                              <Option value="자기소개서">📝 자기소개서</Option>
                              <Option value="사전과제">📋 사전과제</Option>
                              <Option value="포트폴리오">🎨 포트폴리오</Option>
                              <Option value="논문/연구자료">📚 논문/연구자료</Option>
                              <Option value="기타">📎 기타</Option>
                            </Select>
                          </div>
                        )}
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        )}

        {/* 사용자 의도 선택 */}
        <div style={{ marginBottom: '16px' }}>
          <Text strong>분석 목적</Text>
          <Select
            value={userIntent}
            onChange={setUserIntent}
            style={{ width: '100%', marginTop: '8px' }}
            placeholder="분석 목적을 선택하세요"
          >
            <Option value="면접 준비">🎯 면접 준비</Option>
            <Option value="문서 요약">📝 문서 요약</Option>
            <Option value="키워드 추출">🔍 키워드 추출</Option>
            <Option value="내용 분석">📊 내용 분석</Option>
            <Option value="기타">⚙️ 기타</Option>
          </Select>
        </div>

        {/* 추가 컨텍스트 입력 */}
        <div style={{ marginBottom: '20px' }}>
          <Text strong>추가 요청사항 (선택사항)</Text>
          <TextArea
            value={additionalContext}
            onChange={(e) => setAdditionalContext(e.target.value)}
            placeholder="예: 특정 분야의 면접을 준비 중입니다, 특별히 주목해야 할 부분이 있습니다 등"
            rows={3}
            style={{ marginTop: '8px' }}
          />
        </div>

        {/* 업로드 진행률 */}
        {uploadMutation.isLoading && (
          <Progress
            percent={uploadProgress}
            status="active"
            style={{ marginBottom: '16px' }}
          />
        )}

        {/* 업로드 버튼 */}
        <Button
          type="primary"
          size="large"
          icon={<CloudUploadOutlined />}
          onClick={handleUpload}
          loading={uploadMutation.isLoading}
          disabled={files.length === 0}
          style={{ width: '100%' }}
        >
          {uploadMutation.isLoading ? '업로드 중...' : `${files.length}개 파일 업로드`}
        </Button>
      </Card>
    </div>
  );
};

export default DocumentUpload; 