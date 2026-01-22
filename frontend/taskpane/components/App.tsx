import * as React from 'react';
import { useState } from 'react';
import { PdfUpload } from './PdfUpload';
import { ErrorChecker } from './ErrorChecker';
import { ModelChat } from './ModelChat';
import './App.css';

type Tab = 'upload' | 'errors' | 'chat';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<Tab>('upload');
  const [modelExists, setModelExists] = useState(false);

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>DCF Assistant</h1>
        <p className="subtitle">AI-Powered Financial Modeling</p>
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
          disabled={!modelExists}
        >
          ✓ Check Errors
        </button>
        <button
          className={`tab-button ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
          disabled={!modelExists}
        >
          💬 Chat
        </button>
      </nav>

      <main className="app-content">
        {activeTab === 'upload' && <PdfUpload onModelCreated={() => setModelExists(true)} />}
        {activeTab === 'errors' && <ErrorChecker />}
        {activeTab === 'chat' && <ModelChat />}
      </main>

      <footer className="app-footer">
        <p>Powered by OpenAI & LangChain</p>
      </footer>
    </div>
  );
};
