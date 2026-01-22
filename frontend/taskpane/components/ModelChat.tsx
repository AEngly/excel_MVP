import * as React from 'react';
import { useState, useRef, useEffect } from 'react';
import axios from 'axios';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export const ModelChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Hi! I can help you understand your DCF model. Ask me about assumptions, results, or sensitivity analysis.'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Extract current model data
      const modelData = await extractModelSnapshot();

      // Send to backend
      const response = await axios.post('http://localhost:3001/api/chat', {
        message: input,
        modelData,
        history: messages
      });

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.response
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  const extractModelSnapshot = async () => {
    return await Excel.run(async (context) => {
      const sheets = context.workbook.worksheets;
      sheets.load('items/name');
      await context.sync();

      const snapshot: any = {};

      for (const sheet of sheets.items) {
        const usedRange = sheet.getUsedRange();
        usedRange.load(['values', 'formulas']);
        await context.sync();

        snapshot[sheet.name] = {
          values: usedRange.values,
          formulas: usedRange.formulas
        };
      }

      return snapshot;
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-container">
      <h2>Model Chat</h2>
      <p style={{ marginBottom: '15px', color: '#666', fontSize: '14px' }}>
        Ask questions about your DCF model, assumptions, or run sensitivity analyses.
      </p>

      <div className="chat-messages">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`chat-message ${msg.role}`}
          >
            {msg.content}
          </div>
        ))}
        {loading && (
          <div className="chat-message assistant">
            <span className="loading-spinner"></span>
            <span style={{ marginLeft: '10px' }}>Thinking...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-wrapper">
        <input
          type="text"
          placeholder="Ask about your model..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={!input.trim() || loading}>
          Send
        </button>
      </div>

      <div style={{ marginTop: '15px', fontSize: '12px', color: '#666' }}>
        <strong>Try asking:</strong>
        <ul style={{ marginTop: '5px', paddingLeft: '20px' }}>
          <li>What's the enterprise value?</li>
          <li>How does WACC affect the valuation?</li>
          <li>What if revenue growth is 15% instead?</li>
        </ul>
      </div>
    </div>
  );
};
