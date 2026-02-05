import * as React from 'react';
import { useState } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';

interface PdfSession {
  sessionId: string;
  filename: string;
  chunks: number;
  uploadedAt: string;
  summary: string;
}

interface PdfUploadProps {
  onModelCreated: () => void;
  sessions: PdfSession[];
  onSessionCreated: (sessionId: string, filename: string, chunks: number, summary: string) => void;
  onSessionRemoved: (sessionId: string) => void;
}

export const PdfUpload: React.FC<PdfUploadProps> = ({ onModelCreated, sessions, onSessionCreated, onSessionRemoved }) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState<{ type: 'success' | 'error' | 'info', message: string } | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setStatus(null);
    } else {
      setStatus({ type: 'error', message: 'Please select a valid PDF file' });
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setStatus({ type: 'info', message: 'Uploading and processing PDF...' });

    try {
      const formData = new FormData();
      formData.append('pdf', file);

      // Send to backend API
      const response = await axios.post(`${API_BASE_URL}/api/upload-pdf`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      console.log('Received upload response:', response.data);
      console.log('Session ID:', response.data.sessionId);
      console.log('Chunks created:', response.data.chunks);

      // Store sessionId for PDF chat context
      if (response.data.sessionId) {
        onSessionCreated(
          response.data.sessionId,
          response.data.filename,
          response.data.chunks,
          response.data.summary || 'No summary available'
        );
        console.log('🔑 Stored session ID:', response.data.sessionId.substring(0, 8) + '...');
      }

      // Reset file input
      setFile(null);
      const fileInput = document.getElementById('pdf-input') as HTMLInputElement;
      if (fileInput) fileInput.value = '';

      setStatus({
        type: 'success',
        message: `✅ ${response.data.filename} uploaded! ${response.data.chunks} chunks ready.`
      });
    } catch (error: any) {
      console.error('Upload error:', error);
      const errorMsg = error.response?.data?.detail || error.message || 'Unknown error';
      setStatus({
        type: 'error',
        message: `Failed to process PDF: ${errorMsg}`
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="upload-container">
      <h2>Upload Company PDF</h2>
      <p style={{ marginBottom: '20px', color: '#666', fontSize: '14px' }}>
        Upload PDFs to make them available for analysis in the Chat tab. The AI will use embeddings to find relevant information.
      </p>

      {/* List of uploaded PDFs */}
      {sessions.length > 0 && (
        <div style={{ marginBottom: '20px', padding: '15px', background: '#f8f9fa', borderRadius: '8px' }}>
          <h3 style={{ margin: '0 0 10px 0', fontSize: '14px', fontWeight: 600 }}>Uploaded PDFs ({sessions.length})</h3>
          {sessions.map((session) => (
            <div
              key={session.sessionId}
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                padding: '12px',
                background: 'white',
                borderRadius: '6px',
                marginBottom: '8px',
                fontSize: '13px'
              }}
            >
              <div style={{ flex: 1, marginRight: '10px' }}>
                <div style={{ fontWeight: 500, marginBottom: '4px' }}>📄 {session.filename}</div>
                <div style={{ fontSize: '12px', color: '#555', marginBottom: '4px', fontStyle: 'italic' }}>
                  {session.summary}
                </div>
                <div style={{ fontSize: '11px', color: '#999' }}>
                  {session.chunks} chunks • {session.uploadedAt}
                </div>
              </div>
              <button
                onClick={() => onSessionRemoved(session.sessionId)}
                style={{
                  background: '#dc3545',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  padding: '6px 12px',
                  cursor: 'pointer',
                  fontSize: '12px'
                }}
              >
                🗑️ Remove
              </button>
            </div>
          ))}
        </div>
      )}

      <div
        className="file-input-wrapper"
        onClick={() => document.getElementById('pdf-input')?.click()}
      >
        <input
          id="pdf-input"
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
        />
        <div style={{ fontSize: '48px', marginBottom: '10px' }}>📄</div>
        <p>{file ? file.name : 'Click to select PDF file'}</p>
        <p style={{ fontSize: '12px', color: '#999', marginTop: '5px' }}>
          Supports: Financial statements, investor presentations, annual reports
        </p>
      </div>

      <button
        className="primary-button"
        onClick={handleUpload}
        disabled={!file || uploading}
      >
        {uploading ? (
          <>
            <span className="loading-spinner"></span>
            <span style={{ marginLeft: '10px' }}>Processing...</span>
          </>
        ) : (
          'Upload PDF'
        )}
      </button>

      {status && (
        <div className={`status-message ${status.type}`}>
          {status.message}
        </div>
      )}
    </div>
  );
};
