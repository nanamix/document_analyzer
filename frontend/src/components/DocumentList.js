import React, { useState } from 'react';
import { 
  Card, 
  List, 
  Button, 
  Typography, 
  Tag, 
  Space, 
  Modal, 
  message,
  Tooltip,
  Empty,
  Spin
} from 'antd';
import { 
  FileTextOutlined, 
  EyeOutlined, 
  DeleteOutlined,
  BarChartOutlined,
  CalendarOutlined,
  FileImageOutlined,
  FilePdfOutlined
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useNavigate } from 'react-router-dom';
import moment from 'moment';
import { documentService, handleApiError } from '../services/api';
import AnalysisModal from './AnalysisModal';

const { Title, Text } = Typography;

const DocumentList = ({ showRecent = false }) => {
  const [selectedDocuments, setSelectedDocuments] = useState([]);
  const [analysisModalVisible, setAnalysisModalVisible] = useState(false);
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // 문서 목록 조회
  const { data: documents = [], isLoading, error } = useQuery(
    'documents',
    () => documentService.getDocuments(0, showRecent ? 5 : 100),
    {
      refetchOnWindowFocus: false,
      retry: 1,
    }
  );

  // 문서 삭제 뮤테이션
  const deleteMutation = useMutation(
    (documentId) => documentService.deleteDocument(documentId),
    {
      onSuccess: () => {
        message.success('문서가 삭제되었습니다');
        queryClient.invalidateQueries('documents');
      },
      onError: (error) => {
        const errorInfo = handleApiError(error);
        message.error(errorInfo.message);
      },
    }
  );

  // 문서 삭제 확인
  const handleDelete = (document) => {
    Modal.confirm({
      title: '문서 삭제',
      content: `"${document.original_filename}" 문서를 삭제하시겠습니까?`,
      okText: '삭제',
      cancelText: '취소',
      okType: 'danger',
      onOk: () => deleteMutation.mutate(document.id),
    });
  };

  // 문서 선택/해제
  const toggleDocumentSelection = (document) => {
    setSelectedDocuments(prev => {
      const isSelected = prev.find(doc => doc.id === document.id);
      if (isSelected) {
        return prev.filter(doc => doc.id !== document.id);
      } else {
        return [...prev, document];
      }
    });
  };

  // 분석 시작
  const handleAnalyze = () => {
    if (selectedDocuments.length === 0) {
      message.warning('분석할 문서를 선택해주세요');
      return;
    }
    setAnalysisModalVisible(true);
  };

  // 파일 타입 아이콘
  const getFileIcon = (fileExtension, fileType) => {
    if (fileType === 'pdf' || fileExtension === 'pdf') {
      return <FilePdfOutlined style={{ color: '#ff4d4f' }} />;
    } else if (fileType === 'image' || ['png', 'jpg', 'jpeg'].includes(fileExtension)) {
      return <FileImageOutlined style={{ color: '#1890ff' }} />;
    }
    return <FileTextOutlined />;
  };

  // 파일 크기 포매팅
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (isLoading) {
    return (
      <div className="loading-spinner">
        <Spin size="large" />
        <Text style={{ marginTop: '16px', display: 'block' }}>문서 목록을 불러오는 중...</Text>
      </div>
    );
  }

  if (error) {
    const errorInfo = handleApiError(error);
    return (
      <div className="error-message">
        ❌ {errorInfo.message}
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <Empty
        image={Empty.PRESENTED_IMAGE_SIMPLE}
        description="업로드된 문서가 없습니다"
        style={{ padding: '40px 0' }}
      >
        {!showRecent && (
          <Button type="primary" onClick={() => navigate('/')}>
            문서 업로드하기
          </Button>
        )}
      </Empty>
    );
  }

  return (
    <div>
      {/* 헤더 */}
      {!showRecent && (
        <div style={{ marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={3}>📁 문서 목록 ({documents.length}개)</Title>
          <Space>
            <Text>선택된 문서: {selectedDocuments.length}개</Text>
            <Button
              type="primary"
              icon={<BarChartOutlined />}
              onClick={handleAnalyze}
              disabled={selectedDocuments.length === 0}
            >
              선택한 문서 분석
            </Button>
          </Space>
        </div>
      )}

      {/* 문서 목록 */}
      <List
        grid={{ gutter: 16, xs: 1, sm: 1, md: 2, lg: 2, xl: 3 }}
        dataSource={documents}
        renderItem={(document) => {
          const isSelected = selectedDocuments.find(doc => doc.id === document.id);
          
          return (
            <List.Item>
              <Card
                className="document-card"
                size="small"
                hoverable
                style={{
                  border: isSelected ? '2px solid #1890ff' : '1px solid #f0f0f0',
                  cursor: 'pointer'
                }}
                onClick={() => !showRecent && toggleDocumentSelection(document)}
                actions={[
                  <Tooltip title="상세보기">
                    <Button
                      type="text"
                      icon={<EyeOutlined />}
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/analysis/${document.id}`);
                      }}
                    />
                  </Tooltip>,
                  <Tooltip title="삭제">
                    <Button
                      type="text"
                      icon={<DeleteOutlined />}
                      danger
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(document);
                      }}
                      loading={deleteMutation.isLoading}
                    />
                  </Tooltip>
                ]}
              >
                <Card.Meta
                  avatar={getFileIcon(document.file_extension, document.file_type)}
                  title={
                    <div>
                      <Text strong style={{ fontSize: '14px' }}>
                        {document.original_filename}
                      </Text>
                      {isSelected && (
                        <Tag color="blue" style={{ marginLeft: '8px' }}>선택됨</Tag>
                      )}
                    </div>
                  }
                  description={
                    <Space direction="vertical" size="small" style={{ width: '100%' }}>
                      <Space>
                        <Tag color={document.file_type === 'pdf' ? 'red' : 'blue'}>
                          {document.file_extension.toUpperCase()}
                        </Tag>
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          {formatFileSize(document.file_size)}
                        </Text>
                      </Space>
                      
                      {document.user_intent && (
                        <Tag color="green">{document.user_intent}</Tag>
                      )}
                      
                      <Space size="small">
                        <CalendarOutlined style={{ fontSize: '12px', color: '#999' }} />
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          {moment(document.created_at).format('YYYY-MM-DD HH:mm')}
                        </Text>
                      </Space>

                      {document.keywords && document.keywords.length > 0 && (
                        <div>
                          <Text type="secondary" style={{ fontSize: '12px' }}>키워드: </Text>
                          {document.keywords.slice(0, 3).map((keyword, index) => (
                            <span key={index} className="keyword-tag">
                              {keyword}
                            </span>
                          ))}
                          {document.keywords.length > 3 && (
                            <span className="keyword-tag">+{document.keywords.length - 3}</span>
                          )}
                        </div>
                      )}
                    </Space>
                  }
                />
              </Card>
            </List.Item>
          );
        }}
      />

      {/* 분석 모달 */}
      <AnalysisModal
        visible={analysisModalVisible}
        onCancel={() => setAnalysisModalVisible(false)}
        documents={selectedDocuments}
        onSuccess={() => {
          setAnalysisModalVisible(false);
          setSelectedDocuments([]);
        }}
      />
    </div>
  );
};

export default DocumentList; 