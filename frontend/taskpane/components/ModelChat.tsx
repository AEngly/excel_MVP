import * as React from 'react';
import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface PdfSession {
  sessionId: string;
  filename: string;
  chunks: number;
  uploadedAt: string;
  summary: string;
}

interface ModelChatProps {
  sessions: PdfSession[];
}

export const ModelChat: React.FC<ModelChatProps> = ({ sessions }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [agentMode, setAgentMode] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    const currentInput = input;
    setInput('');
    setLoading(true);

    try {
      // Always extract Excel model for context
      console.log(agentMode ? '🤖 Agent Mode: Read + Write' : '📖 Read-Only Mode: Read only');
      const modelData = await extractModelSnapshot();
      console.log('✅ Model snapshot extracted:', Object.keys(modelData).length, 'sheets');

      const payload: any = {
        message: currentInput,
        history: messages,
        sessionIds: sessions.map(s => s.sessionId),  // Include all sessionIds for PDF context
        modelData: modelData,  // Always send Excel model data
        agentMode: agentMode  // Tell backend if we can write or just read
      };

      const response = await axios.post(`${API_BASE_URL}/api/chat`, payload);

      console.log('📩 Received response:', response.data);
      console.log('📝 Response text:', response.data.response);
      console.log('⚡ Actions:', response.data.actions);
      console.log('🔍 Type of response.data:', typeof response.data);
      console.log('🔍 Type of response.data.response:', typeof response.data.response);

      // Handle if response.data is a string instead of object
      let parsedData = response.data;
      if (typeof response.data === 'string') {
        console.log('⚠️  Response is a string, parsing...');
        try {
          parsedData = JSON.parse(response.data);
        } catch (e) {
          console.error('Failed to parse response string:', e);
          parsedData = { response: response.data, actions: [] };
        }
      }

      // Ensure we always have a string for content
      let responseText = '';
      if (typeof parsedData.response === 'string') {
        responseText = parsedData.response;
      } else if (parsedData.response) {
        responseText = JSON.stringify(parsedData.response);
      } else {
        // Fallback if no response field
        responseText = JSON.stringify(parsedData);
      }

      const assistantMessage: Message = {
        role: 'assistant',
        content: responseText
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Execute any actions returned by AI (only in Agent Mode)
      if (parsedData.actions && parsedData.actions.length > 0) {
        if (agentMode) {
          console.log('🤖 Agent Mode: Executing', parsedData.actions.length, 'actions');

          // Log each action for debugging
          parsedData.actions.forEach((action: any, idx: number) => {
            console.log(`Action ${idx + 1}:`, action.type);
            if (action.range && action.values) {
              console.log(`  Range: ${action.range}`);
              console.log(`  Values dimensions: ${action.values.length} rows x ${action.values[0]?.length || 0} cols`);
              console.log(`  Values:`, action.values);
            }
          });

          await executeActions(parsedData.actions);
        } else {
          console.log('📖 Read-Only Mode: Ignoring', parsedData.actions.length, 'actions (switch to Agent Mode to execute)');
        }
      }
    } catch (error: any) {
      console.error('Chat error:', error);

      let errorMsg = 'Unknown error occurred';

      // Check for different error types
      if (error.response) {
        // Backend returned an error response
        const status = error.response.status;
        const detail = error.response.data?.detail || error.response.data?.message;

        if (status === 500 && detail) {
          // Backend error - likely OpenAI API issue
          if (detail.includes('API key') || detail.includes('authentication') || detail.includes('Unauthorized')) {
            errorMsg = '🔑 OpenAI API Key Error: Invalid or missing API key. Check backend .env file.';
          } else if (detail.includes('rate limit') || detail.includes('quota')) {
            errorMsg = '⏱️ OpenAI Rate Limit: Too many requests or quota exceeded. Wait and try again.';
          } else if (detail.includes('timeout') || detail.includes('timed out')) {
            errorMsg = '⏱️ OpenAI Timeout: Request took too long. Try a simpler question.';
          } else {
            errorMsg = `🤖 OpenAI API Error: ${detail}`;
          }
        } else if (status === 400) {
          errorMsg = `❌ Bad Request: ${detail || 'Invalid request format'}`;
        } else {
          errorMsg = `❌ Backend Error (${status}): ${detail || 'Unknown error'}`;
        }
      } else if (error.request) {
        // Request made but no response
        errorMsg = '🔌 Network Error: Cannot reach backend. Is the backend server running on https://localhost:3001?';
      } else {
        // Something else happened
        errorMsg = `❌ Error: ${error.message}`;
      }

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: errorMsg
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
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
        usedRange.load(['values', 'formulas', 'numberFormat', 'address', 'rowCount', 'columnCount', 'rowIndex', 'columnIndex']);
        await context.sync();

        const values = usedRange.values;
        const formulas = usedRange.formulas;
        const numberFormat = usedRange.numberFormat;
        const rowCount = usedRange.rowCount;
        const colCount = usedRange.columnCount;
        const startRow = usedRange.rowIndex;  // Absolute row in Excel (0-based)
        const startCol = usedRange.columnIndex;  // Absolute col in Excel (0-based)

        // Build sparse representation - only non-empty cells
        const cells: any[] = [];

        for (let row = 0; row < rowCount; row++) {
          for (let col = 0; col < colCount; col++) {
            const value = values[row][col];
            const formula = formulas[row][col];

            // Skip completely empty cells
            if ((value === "" || value === null) && (formula === "" || formula === null)) {
              continue;
            }

            // Load formatting for this specific cell
            const cell = usedRange.getCell(row, col);
            cell.format.load(['font/bold', 'font/color', 'fill/color']);
            await context.sync();

            cells.push({
              row: startRow + row,  // Absolute row number in Excel
              col: startCol + col,  // Absolute column number in Excel
              value: value,
              formula: formula || null,
              numberFormat: numberFormat[row][col],
              bold: cell.format.font.bold,
              fontColor: cell.format.font.color,
              fillColor: cell.format.fill.color
            });
          }
        }

        snapshot[sheet.name] = {
          cells: cells,  // Sparse format
          address: usedRange.address
        };
      }

      return snapshot;
    });
  };

  const executeActions = async (actions: any[]) => {
    // Helper function to convert column letter to number (A=1, B=2, etc.)
    const colToNum = (col: string): number => {
      let num = 0;
      for (let i = 0; i < col.length; i++) {
        num = num * 26 + (col.charCodeAt(i) - 64);
      }
      return num;
    };

    await Excel.run(async (context) => {
      for (const action of actions) {
        try {
          const sheet = context.workbook.worksheets.getItem(action.sheet);

          if (action.type === 'setCellValue') {
            const cell = sheet.getRange(action.cell);
            cell.values = [[action.value]];
          }
          else if (action.type === 'setFormula') {
            const cell = sheet.getRange(action.cell);
            cell.formulas = [[action.formula]];
          }
          else if (action.type === 'setRangeValues') {
            // Parse range to get dimensions
            const rangeParts = action.range.split(':');
            if (rangeParts.length === 2) {
              const [startCell, endCell] = rangeParts;
              const startCol = startCell.match(/[A-Z]+/)[0];
              const startRow = parseInt(startCell.match(/\d+/)[0]);
              const endCol = endCell.match(/[A-Z]+/)[0];
              const endRow = parseInt(endCell.match(/\d+/)[0]);

              // Calculate expected dimensions
              const expectedRows = endRow - startRow + 1;
              const expectedCols = colToNum(endCol) - colToNum(startCol) + 1;
              const actualRows = action.values.length;
              const actualCols = action.values[0]?.length || 0;

              console.log(`📐 Range ${action.range}: expecting ${expectedRows}x${expectedCols}, got ${actualRows}x${actualCols}`);

              if (expectedRows !== actualRows || expectedCols !== actualCols) {
                throw new Error(`Dimension mismatch: range ${action.range} expects ${expectedRows}x${expectedCols}, but values are ${actualRows}x${actualCols}`);
              }
            }

            const range = sheet.getRange(action.range);
            range.values = action.values;
          }
          else if (action.type === 'setRangeFormulas') {
            const range = sheet.getRange(action.range);
            range.formulas = action.formulas;
          }
          else if (action.type === 'clearRange') {
            const range = sheet.getRange(action.range);
            range.clear('Contents');
          }
          else if (action.type === 'formatCell') {
            const cell = sheet.getRange(action.cell);
            if (action.format.bold) cell.format.font.bold = true;
            if (action.format.numberFormat) cell.numberFormat = action.format.numberFormat;
            if (action.format.bgColor) cell.format.fill.color = action.format.bgColor;
            if (action.format.fontColor) cell.format.font.color = action.format.fontColor;
          }
        } catch (err) {
          console.error('Action failed:', action, err);
          throw err; // Re-throw to show user
        }
      }
      await context.sync();
      console.log('✅ All actions executed successfully!');
    });
  };

  return (
    <div className="chat-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
        <h2 style={{ margin: 0 }}>Model Chat</h2>
        <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={agentMode}
            onChange={(e) => setAgentMode(e.target.checked)}
            style={{ marginRight: '8px' }}
          />
          <span style={{ fontSize: '14px', fontWeight: 500 }}>
            {agentMode ? '🤖 Agent Mode (Read + Write)' : '📖 Read-Only Mode'}
          </span>
        </label>
      </div>
      <p style={{ marginBottom: '15px', color: '#666', fontSize: '14px' }}>
        {agentMode
          ? '🤖 AI can read your Excel model and make changes'
          : '📖 AI can read your Excel model but won\'t make changes (read-only)'}
        {sessions.length > 0 && ` 📚 ${sessions.length} PDF${sessions.length > 1 ? 's' : ''} available for reference.`}
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
