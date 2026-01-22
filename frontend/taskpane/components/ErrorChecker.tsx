import * as React from 'react';
import { useState } from 'react';
import axios from 'axios';

interface ErrorItem {
  sheet: string;
  cell: string;
  type: 'formula' | 'circular' | 'missing' | 'inconsistent';
  severity: 'critical' | 'warning';
  message: string;
}

export const ErrorChecker: React.FC = () => {
  const [checking, setChecking] = useState(false);
  const [errors, setErrors] = useState<ErrorItem[]>([]);
  const [status, setStatus] = useState<string>('');

  const runErrorCheck = async () => {
    setChecking(true);
    setStatus('Analyzing model...');
    setErrors([]);

    try {
      // Extract model data from Excel
      const modelData = await extractModelData();

      // Send to backend for analysis
      const response = await axios.post('http://localhost:3001/api/check-errors', {
        modelData
      });

      setErrors(response.data.errors || []);
      setStatus(
        response.data.errors.length === 0
          ? 'No errors found! Model looks good.'
          : `Found ${response.data.errors.length} issue(s)`
      );
    } catch (error) {
      console.error('Error checking:', error);
      setStatus('Failed to check errors. Please try again.');
    } finally {
      setChecking(false);
    }
  };

  const extractModelData = async () => {
    return await Excel.run(async (context) => {
      const sheets = context.workbook.worksheets;
      sheets.load('items/name');
      await context.sync();

      const modelData: any = {};

      for (const sheet of sheets.items) {
        const usedRange = sheet.getUsedRange();
        usedRange.load(['values', 'formulas', 'address']);
        await context.sync();

        modelData[sheet.name] = {
          values: usedRange.values,
          formulas: usedRange.formulas,
          address: usedRange.address
        };
      }

      return modelData;
    });
  };

  const navigateToError = async (error: ErrorItem) => {
    await Excel.run(async (context) => {
      const sheet = context.workbook.worksheets.getItem(error.sheet);
      sheet.activate();

      const range = sheet.getRange(error.cell);
      range.select();

      await context.sync();
    });
  };

  return (
    <div className="error-container">
      <h2>Error Checker</h2>
      <p style={{ marginBottom: '20px', color: '#666', fontSize: '14px' }}>
        Validates formulas, cross-references, and calculations across all worksheets.
      </p>

      <button
        className="primary-button"
        onClick={runErrorCheck}
        disabled={checking}
      >
        {checking ? (
          <>
            <span className="loading-spinner"></span>
            <span style={{ marginLeft: '10px' }}>Checking...</span>
          </>
        ) : (
          '🔍 Run Error Check'
        )}
      </button>

      {status && (
        <div className={`status-message ${errors.length === 0 ? 'success' : 'info'}`}>
          {status}
        </div>
      )}

      {errors.length > 0 && (
        <div style={{ marginTop: '20px' }}>
          <h3>Issues Found:</h3>
          <ul className="error-list">
            {errors.map((error, index) => (
              <li
                key={index}
                className={`error-item ${error.severity}`}
                onClick={() => navigateToError(error)}
                style={{ cursor: 'pointer' }}
              >
                <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
                  {error.sheet} - {error.cell}
                  <span style={{
                    marginLeft: '8px',
                    fontSize: '11px',
                    padding: '2px 6px',
                    background: error.severity === 'critical' ? '#dc3545' : '#ffc107',
                    color: 'white',
                    borderRadius: '3px'
                  }}>
                    {error.severity.toUpperCase()}
                  </span>
                </div>
                <div style={{ fontSize: '13px' }}>{error.message}</div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
