import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout, Typography, Space } from 'antd';
import { FileTextOutlined } from '@ant-design/icons';
import DocumentUpload from './components/DocumentUpload';
import DocumentList from './components/DocumentList';
import AnalysisResults from './components/AnalysisResults';
import './App.css';

const { Header, Content, Footer } = Layout;
const { Title } = Typography;

function App() {
  return (
    <div className="app-container">
      <Layout style={{ minHeight: '100vh', background: 'transparent' }}>
        <Header style={{ 
          background: 'rgba(255, 255, 255, 0.95)', 
          backdropFilter: 'blur(10px)',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            height: '100%'
          }}>
            <Space size="middle">
              <FileTextOutlined style={{ fontSize: '24px', color: '#1890ff' }} />
              <Title level={3} style={{ margin: 0, color: '#1890ff' }}>
                Document Analyzer
              </Title>
            </Space>
          </div>
        </Header>
        
        <Content className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/documents" element={<DocumentList />} />
            <Route path="/analysis/:documentId" element={<AnalysisResults />} />
          </Routes>
        </Content>
        
        <Footer style={{ 
          textAlign: 'center', 
          background: 'rgba(255, 255, 255, 0.8)',
          backdropFilter: 'blur(10px)'
        }}>
          Document Analyzer ©2025 - AI를 활용한 문서 분석 시스템
        </Footer>
      </Layout>
    </div>
  );
}

// 홈페이지 컴포넌트
function HomePage() {
  return (
    <div>
      <div className="upload-area">
        <Title level={2} style={{ textAlign: 'center', marginBottom: '30px' }}>
          📄 문서를 업로드하고 AI 분석을 받아보세요
        </Title>
        <DocumentUpload />
      </div>
      
      <div className="analysis-results">
        <Title level={3} style={{ marginBottom: '20px' }}>
          📋 최근 업로드된 문서
        </Title>
        <DocumentList showRecent={true} />
      </div>
    </div>
  );
}

export default App; 