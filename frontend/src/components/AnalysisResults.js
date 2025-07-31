import React from 'react';
import { 
  Card, 
  Typography, 
  Tag, 
  List, 
  Space, 
  Button, 
  Spin, 
  Alert,
  Divider,
  Row,
  Col,
  Statistic
} from 'antd';
import { 
  FileTextOutlined, 
  BulbOutlined, 
  QuestionCircleOutlined,
  KeyOutlined,
  BookOutlined,
  RobotOutlined,
  ArrowLeftOutlined,
  CalendarOutlined
} from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from 'react-query';
import moment from 'moment';
import { documentService, handleApiError } from '../services/api';

const { Title, Text, Paragraph } = Typography;

const AnalysisResults = () => {
  const { documentId } = useParams();
  const navigate = useNavigate();

  // 문서 정보 조회
  const { data: document, isLoading: documentLoading } = useQuery(
    ['document', documentId],
    () => documentService.getDocument(documentId),
    {
      enabled: !!documentId,
      retry: 1,
    }
  );

  // 분석 결과 조회
  const { data: analysisData, isLoading: analysisLoading, error } = useQuery(
    ['analysis', documentId],
    () => documentService.getDocumentAnalysis(documentId),
    {
      enabled: !!documentId,
      retry: 1,
    }
  );

  const isLoading = documentLoading || analysisLoading;

  if (isLoading) {
    return (
      <div className="loading-spinner">
        <Spin size="large" />
        <Text style={{ marginTop: '16px', display: 'block' }}>분석 결과를 불러오는 중...</Text>
      </div>
    );
  }

  if (error) {
    const errorInfo = handleApiError(error);
    return (
      <div>
        <Button 
          icon={<ArrowLeftOutlined />} 
          onClick={() => navigate(-1)}
          style={{ marginBottom: '20px' }}
        >
          돌아가기
        </Button>
        <Alert
          message="분석 결과를 불러올 수 없습니다"
          description={errorInfo.message}
          type="error"
          showIcon
        />
      </div>
    );
  }

  if (!document || !analysisData) {
    return (
      <div>
        <Button 
          icon={<ArrowLeftOutlined />} 
          onClick={() => navigate(-1)}
          style={{ marginBottom: '20px' }}
        >
          돌아가기
        </Button>
        <Alert
          message="문서 또는 분석 결과를 찾을 수 없습니다"
          type="warning"
          showIcon
        />
      </div>
    );
  }

  const analysis = analysisData.analysis || {};

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto' }}>
      {/* 헤더 */}
      <div style={{ marginBottom: '24px' }}>
        <Button 
          icon={<ArrowLeftOutlined />} 
          onClick={() => navigate(-1)}
          style={{ marginBottom: '16px' }}
        >
          돌아가기
        </Button>
        
        <Card>
          <Row gutter={[16, 16]} align="middle">
            <Col flex="auto">
              <Space direction="vertical" size="small">
                <Title level={3} style={{ margin: 0 }}>
                  <FileTextOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
                  {document.original_filename}
                </Title>
                <Space wrap>
                  <Tag color={document.file_type === 'pdf' ? 'red' : 'blue'}>
                    {document.file_extension.toUpperCase()}
                  </Tag>
                  {document.user_intent && (
                    <Tag color="green">{document.user_intent}</Tag>
                  )}
                  <Tag icon={<RobotOutlined />} color="purple">
                    {analysisData.ai_model?.toUpperCase() || 'AI 분석'}
                  </Tag>
                </Space>
                <Space size="small">
                  <CalendarOutlined style={{ color: '#999' }} />
                  <Text type="secondary">
                    분석일: {moment(document.updated_at || document.created_at).format('YYYY-MM-DD HH:mm')}
                  </Text>
                </Space>
              </Space>
            </Col>
            
            {/* 통계 정보 */}
            <Col>
              <Row gutter={16}>
                {analysis.total_documents && (
                  <Col>
                    <Statistic
                      title="분석 문서 수"
                      value={analysis.total_documents}
                      suffix="개"
                    />
                  </Col>
                )}
                {analysis.total_characters && (
                  <Col>
                    <Statistic
                      title="총 문자 수"
                      value={analysis.total_characters}
                      suffix="자"
                    />
                  </Col>
                )}
              </Row>
            </Col>
          </Row>
        </Card>
      </div>

      {/* 분석 결과 */}
      <Row gutter={[16, 16]}>
        {/* 키워드 */}
        <Col xs={24} lg={12}>
          <Card
            title={
              <Space>
                <KeyOutlined style={{ color: '#1890ff' }} />
                <span>주요 키워드</span>
              </Space>
            }
            size="small"
          >
            {analysis.keywords && analysis.keywords.length > 0 ? (
              <div>
                {analysis.keywords.map((keyword, index) => (
                  <span key={index} className="keyword-tag">
                    {keyword}
                  </span>
                ))}
              </div>
            ) : (
              <Text type="secondary">키워드가 추출되지 않았습니다</Text>
            )}
          </Card>
        </Col>

        {/* 문서 유형 */}
        <Col xs={24} lg={12}>
          <Card
            title={
              <Space>
                <BookOutlined style={{ color: '#52c41a' }} />
                <span>문서 분류</span>
              </Space>
            }
            size="small"
          >
            <Tag color="blue" style={{ fontSize: '14px', padding: '4px 12px' }}>
              {analysis.document_type || '일반 문서'}
            </Tag>
          </Card>
        </Col>

        {/* 주요 주제 */}
        <Col xs={24}>
          <Card
            title={
              <Space>
                <BulbOutlined style={{ color: '#faad14' }} />
                <span>주요 주제</span>
              </Space>
            }
            size="small"
          >
            {analysis.main_topics && analysis.main_topics.length > 0 ? (
              <List
                grid={{ gutter: 8, xs: 1, sm: 2, md: 3 }}
                dataSource={analysis.main_topics}
                renderItem={(topic, index) => (
                  <List.Item>
                    <Tag color="geekblue" style={{ margin: '2px', padding: '4px 8px' }}>
                      {index + 1}. {topic}
                    </Tag>
                  </List.Item>
                )}
              />
            ) : (
              <Text type="secondary">주요 주제가 식별되지 않았습니다</Text>
            )}
          </Card>
        </Col>

        {/* 문서 요약 */}
        <Col xs={24}>
          <Card title="📄 문서 요약" size="small">
            {analysis.summary ? (
              <Paragraph style={{ fontSize: '14px', lineHeight: '1.6' }}>
                {analysis.summary}
              </Paragraph>
            ) : (
              <Text type="secondary">요약 정보가 없습니다</Text>
            )}
          </Card>
        </Col>

        {/* 추천사항 */}
        <Col xs={24}>
          <Card title="💡 추천사항" size="small">
            {analysis.recommendations && analysis.recommendations.length > 0 ? (
              <List
                dataSource={analysis.recommendations}
                renderItem={(recommendation, index) => (
                  <List.Item>
                    <Text>
                      <strong>{index + 1}.</strong> {recommendation}
                    </Text>
                  </List.Item>
                )}
              />
            ) : (
              <Text type="secondary">추천사항이 없습니다</Text>
            )}
          </Card>
        </Col>

        {/* 면접 예상 질문 */}
        {analysis.interview_questions && analysis.interview_questions.length > 0 && (
          <Col xs={24}>
            <Card
              title={
                <Space>
                  <QuestionCircleOutlined style={{ color: '#f5222d' }} />
                  <span>면접 예상 질문</span>
                </Space>
              }
              size="small"
            >
              <List
                dataSource={analysis.interview_questions}
                renderItem={(question, index) => (
                  <List.Item>
                    <div className="interview-question">
                      <Text strong style={{ color: '#1890ff' }}>
                        Q{index + 1}.
                      </Text>
                      <Text style={{ marginLeft: '8px' }}>{question}</Text>
                    </div>
                  </List.Item>
                )}
              />
            </Card>
          </Col>
        )}
      </Row>

      {/* 원본 AI 응답 (디버깅용, 개발 환경에서만) */}
      {process.env.NODE_ENV === 'development' && analysisData.raw_response && (
        <Card
          title="🔧 원본 AI 응답 (개발 모드)"
          size="small"
          style={{ marginTop: '16px' }}
        >
          <pre style={{ 
            fontSize: '12px', 
            background: '#f6f8fa', 
            padding: '12px', 
            borderRadius: '4px',
            overflow: 'auto',
            maxHeight: '300px'
          }}>
            {JSON.stringify(analysisData.raw_response, null, 2)}
          </pre>
        </Card>
      )}
    </div>
  );
};

export default AnalysisResults; 