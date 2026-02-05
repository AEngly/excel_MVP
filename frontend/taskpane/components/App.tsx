import * as React from 'react';
import { useState } from 'react';
import { PdfUpload } from './PdfUpload';
import { ErrorChecker } from './ErrorChecker';
import { ModelChat } from './ModelChat';
import { API_BASE_URL } from '../config';
import './App.css';

type Tab = 'upload' | 'errors' | 'chat';

interface PdfSession {
  sessionId: string;
  filename: string;
  chunks: number;
  uploadedAt: string;
  summary: string;
}

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<Tab>('upload');
  const [modelExists, setModelExists] = useState(false);
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [sessions, setSessions] = useState<PdfSession[]>([]);
  const [errorMsg, setErrorMsg] = useState<string>('');

  React.useEffect(() => {
    const checkBackend = async () => {
      try {
        console.log('Checking backend at:', `${API_BASE_URL}/health`);
        const response = await fetch(`${API_BASE_URL}/health`, {
          mode: 'cors',
          credentials: 'omit'
        });
        console.log('Backend response:', response.status);
        if (response.ok) {
          setBackendStatus('online');
          setErrorMsg('');
        } else {
          setBackendStatus('offline');
          setErrorMsg(`HTTP ${response.status}`);
        }
      } catch (err: any) {
        console.error('Backend error:', err);
        setBackendStatus('offline');
        setErrorMsg(err.message || 'Network error');
      }
    };
    checkBackend();
  }, []);

  const addSession = (sessionId: string, filename: string, chunks: number, summary: string) => {
    const newSession: PdfSession = {
      sessionId,
      filename,
      chunks,
      uploadedAt: new Date().toLocaleString(),
      summary
    };
    setSessions(prev => [...prev, newSession]);
    console.log('📚 Added session:', filename);
  };

  const removeSession = (sessionId: string) => {
    setSessions(prev => prev.filter(s => s.sessionId !== sessionId));
    console.log('🗑️ Removed session:', sessionId.substring(0, 8));
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>DCF Assistant</h1>
        <p className="subtitle">AI-Powered Financial Modeling</p>
        <div style={{ fontSize: '12px', marginTop: '5px' }}>
          Backend: <span style={{ color: backendStatus === 'online' ? '#28a745' : backendStatus === 'offline' ? '#dc3545' : '#ffc107' }}>
            {backendStatus === 'online' ? '🟢 Online' : backendStatus === 'offline' ? '🔴 Offline' : '🟡 Checking...'}
          </span>
          <br />
          <small style={{ fontSize: '10px', color: '#666' }}>API: {API_BASE_URL}</small>
          {errorMsg && <><br /><small style={{ fontSize: '10px', color: '#dc3545' }}>Error: {errorMsg}</small></>}
        </div>
      </header>

      <nav className="tab-nav">
        <button
          className={`tab-button ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setActiveTab('upload')}
        >
          📄 Upload PDF
        </button>
        <button
          className={`tab-button ${activeTab === 'errors' ? 'active' : ''}`}
          onClick={() => setActiveTab('errors')}
        >
          ✓ Check Errors
        </button>
        <button
          className={`tab-button ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          💬 Chat
        </button>
      </nav>

      <main className="app-content">
        {activeTab === 'upload' && (
          <PdfUpload
            onModelCreated={() => setModelExists(true)}
            sessions={sessions}
            onSessionCreated={addSession}
            onSessionRemoved={removeSession}
          />
        )}
        {activeTab === 'errors' && <ErrorChecker />}
        {activeTab === 'chat' && <ModelChat sessions={sessions} />}
      </main>

      <footer className="app-footer">
        <p>Powered by OpenAI & LangChain</p>
      </footer>
    </div>
  );
};
