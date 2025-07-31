import React, { useState } from 'react';
import { 
  Modal, 
  Form, 
  Select, 
  Input, 
  List, 
  Typography, 
  Tag, 
  Space,
  message,
  Button,
  Alert,
  Checkbox,
  Divider
} from 'antd';
import { 
  RobotOutlined, 
  FileTextOutlined, 
  BulbOutlined,
  SettingOutlined,
  SafetyOutlined,
  WarningOutlined,
  LockOutlined
} from '@ant-design/icons';
import { useMutation, useQueryClient } from 'react-query';
import { useNavigate } from 'react-router-dom';
import { documentService, handleApiError } from '../services/api';

const { Option } = Select;
const { TextArea } = Input;
const { Title, Text } = Typography;

const AnalysisModal = ({ visible, onCancel, documents, onSuccess }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [selectedAI, setSelectedAI] = useState('local');
  const [userConsent, setUserConsent] = useState(false);
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // 분석 뮤테이션
  const analysisMutation = useMutation(
    ({ documentIds, userIntent, aiModel, additionalContext, userConsent }) =>
      documentService.analyzeDocuments(documentIds, userIntent, aiModel, additionalContext, userConsent),
    {
      onSuccess: (data) => {
        message.success('문서 분석이 완료되었습니다!');
        queryClient.invalidateQueries('documents');
        onSuccess();
        
        // 분석 결과 페이지로 이동
        if (data.document_id) {
          navigate(`/analysis/${data.document_id}`);
        }
      },
      onError: (error) => {
        const errorInfo = handleApiError(error);
        message.error(errorInfo.message);
      },
      onSettled: () => {
        setLoading(false);
      }
    }
  );

  // 분석 실행
  const handleAnalyze = async (values) => {
    // 🔒 보안 체크
    if (isExternalAI(values.aiModel) && !userConsent) {
      message.error('외부 AI 사용에 대한 동의가 필요합니다.');
      return;
    }

    setLoading(true);
    
    const documentIds = documents.map(doc => doc.id);
    
    try {
      await analysisMutation.mutateAsync({
        documentIds,
        userIntent: values.userIntent,
        aiModel: values.aiModel,
        additionalContext: values.additionalContext || '',
        userConsent: userConsent
      });
    } catch (error) {
      console.error('Analysis error:', error);
    }
  };

  // 모달 닫기
  const handleCancel = () => {
    if (!loading) {
      form.resetFields();
      setSelectedAI('local');
      setUserConsent(false);
      onCancel();
    }
  };

  // 외부 AI 여부 확인
  const isExternalAI = (model) => {
    return ['openai', 'claude', 'deepseek'].includes(model);
  };

  // AI 모델 선택 핸들러
  const handleAIModelChange = (value) => {
    setSelectedAI(value);
    if (!isExternalAI(value)) {
      setUserConsent(false);
    }
  };

  // AI 모델 옵션 (보안 우선 순서)
  const aiModelOptions = [
    { 
      value: 'local', 
      label: '🔒 로컬 분석 (추천)', 
      icon: '🛡️', 
      description: '가장 안전 - 데이터가 외부로 전송되지 않음',
      security: 'high'
    },
    { 
      value: 'ollama', 
      label: '🏠 Ollama (로컬 AI)', 
      icon: '🤖', 
      description: '로컬 AI 모델 - 인터넷 연결 불필요',
      security: 'high'
    },
    { 
      value: 'openai', 
      label: '⚠️ OpenAI GPT-4', 
      icon: '🌐', 
      description: '외부 서버 전송 - 높은 성능',
      security: 'low'
    },
    { 
      value: 'claude', 
      label: '⚠️ Anthropic Claude', 
      icon: '🧠', 
      description: '외부 서버 전송 - 창의적 분석',
      security: 'low'
    },
    { 
      value: 'deepseek', 
      label: '⚠️ DeepSeek', 
      icon: '🔍', 
      description: '외부 서버 전송 - 비용 효율적',
      security: 'low'
    }
  ];

  return (
    <Modal
      title={
        <Space>
                                <SafetyOutlined style={{ color: '#1890ff' }} />
          <span>🔒 보안 우선 문서 분석</span>
        </Space>
      }
      open={visible}
      onCancel={handleCancel}
      width={700}
      footer={[
        <Button key="cancel" onClick={handleCancel} disabled={loading}>
          취소
        </Button>,
        <Button
          key="analyze"
          type="primary"
          icon={<BulbOutlined />}
          loading={loading}
          onClick={() => form.submit()}
          disabled={isExternalAI(selectedAI) && !userConsent}
        >
          분석 시작
        </Button>
      ]}
    >
      {/* 보안 알림 */}
      <Alert
        message="🔒 데이터 보안 안내"
        description="기본적으로 모든 분석은 로컬에서 수행되며, 문서 내용이 외부 서버로 전송되지 않습니다."
        type="success"
        showIcon
        style={{ marginBottom: '20px' }}
      />

      <div style={{ marginBottom: '20px' }}>
        <Title level={5}>📄 선택된 문서 ({documents.length}개)</Title>
        <List
          size="small"
          dataSource={documents}
          renderItem={(document) => (
            <List.Item>
              <List.Item.Meta
                avatar={<FileTextOutlined />}
                title={document.original_filename}
                description={
                  <Space>
                    <Tag color={document.file_type === 'pdf' ? 'red' : 'blue'}>
                      {document.file_extension.toUpperCase()}
                    </Tag>
                    {document.user_intent && (
                      <Tag color="green">{document.user_intent}</Tag>
                    )}
                  </Space>
                }
              />
            </List.Item>
          )}
        />
      </div>

      <Form
        form={form}
        layout="vertical"
        onFinish={handleAnalyze}
        initialValues={{
          userIntent: '면접 준비',
          aiModel: 'local'
        }}
      >
        <Form.Item
          name="userIntent"
          label={
            <Space>
              <SettingOutlined />
              <span>분석 목적</span>
            </Space>
          }
          rules={[{ required: true, message: '분석 목적을 선택해주세요' }]}
        >
          <Select placeholder="분석 목적을 선택하세요">
            <Option value="면접 준비">🎯 면접 준비</Option>
            <Option value="문서 요약">📝 문서 요약</Option>
            <Option value="키워드 추출">🔍 키워드 추출</Option>
            <Option value="내용 분석">📊 내용 분석</Option>
            <Option value="기타">⚙️ 기타</Option>
          </Select>
        </Form.Item>

        <Form.Item
          name="aiModel"
          label={
            <Space>
              <SafetyOutlined />
              <span>AI 모델 선택 (보안 수준 순)</span>
            </Space>
          }
          rules={[{ required: true, message: 'AI 모델을 선택해주세요' }]}
        >
          <Select 
            placeholder="AI 모델을 선택하세요"
            onChange={handleAIModelChange}
          >
            {aiModelOptions.map(option => (
              <Option key={option.value} value={option.value}>
                <Space direction="vertical" size="small" style={{ width: '100%' }}>
                  <Space>
                    <span>{option.icon}</span>
                    <span>{option.label}</span>
                    {option.security === 'high' && (
                      <Tag color="green" size="small">안전</Tag>
                    )}
                    {option.security === 'low' && (
                      <Tag color="red" size="small">주의</Tag>
                    )}
                  </Space>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {option.description}
                  </Text>
                </Space>
              </Option>
            ))}
          </Select>
        </Form.Item>

        {/* 외부 AI 사용 시 경고 및 동의 */}
        {isExternalAI(selectedAI) && (
          <>
            <Alert
              message="⚠️ 보안 경고"
              description={
                <div>
                  <p><strong>외부 AI 서비스 사용 시 주의사항:</strong></p>
                  <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
                    <li>문서 내용이 외부 서버({selectedAI.toUpperCase()})로 전송됩니다</li>
                    <li>민감한 정보는 자동으로 마스킹되지만 완전하지 않을 수 있습니다</li>
                    <li>외부 서비스의 개인정보 처리방침이 적용됩니다</li>
                    <li>기업 기밀 문서는 로컬 분석을 권장합니다</li>
                  </ul>
                </div>
              }
              type="warning"
              showIcon
              style={{ marginBottom: '16px' }}
            />

            <Form.Item>
              <Checkbox
                checked={userConsent}
                onChange={(e) => setUserConsent(e.target.checked)}
              >
                <Space>
                  <WarningOutlined style={{ color: '#ff4d4f' }} />
                  <span>
                    위 내용을 이해했으며, 문서 내용이 외부 AI 서버로 전송되는 것에 <strong>동의합니다</strong>
                  </span>
                </Space>
              </Checkbox>
            </Form.Item>
          </>
        )}

        {/* 로컬 분석 사용 시 안내 */}
        {!isExternalAI(selectedAI) && (
          <Alert
            message="✅ 안전한 로컬 분석"
            description="선택하신 분석 방법은 문서 내용을 외부로 전송하지 않아 가장 안전합니다."
            type="success"
            showIcon
            style={{ marginBottom: '16px' }}
          />
        )}

        <Form.Item
          name="additionalContext"
          label="추가 요청사항 (선택사항)"
        >
          <TextArea
            rows={3}
            placeholder="예: 기술 면접에 중점을 두어 분석해주세요, 특정 분야의 키워드를 중심으로 분석해주세요 등"
          />
        </Form.Item>
      </Form>

      <Divider />

      <div style={{ 
        background: '#f6f8fa', 
        padding: '16px', 
        borderRadius: '8px',
        border: '1px solid #e1e8ed'
      }}>
        <Space direction="vertical" size="small" style={{ width: '100%' }}>
          <Space>
            <LockOutlined style={{ color: '#1890ff' }} />
            <Text strong>분석 내용</Text>
          </Space>
          <Text type="secondary" style={{ fontSize: '12px' }}>
            • 문서 유형 자동 분류<br/>
            • 주요 키워드 추출 (로컬 처리)<br/>
            • 핵심 주제 파악<br/>
            • 문서 요약<br/>
            • 개선 추천사항<br/>
            • <strong>면접 예상 질문</strong> (면접 준비 선택 시)<br/>
            • 보안 수준 표시
          </Text>
        </Space>
      </div>
    </Modal>
  );
};

export default AnalysisModal; 