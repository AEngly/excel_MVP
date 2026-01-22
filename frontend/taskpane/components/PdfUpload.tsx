import * as React from 'react';
import { useState } from 'react';
import axios from 'axios';

interface PdfUploadProps {
  onModelCreated: () => void;
}

export const PdfUpload: React.FC<PdfUploadProps> = ({ onModelCreated }) => {
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
      const response = await axios.post('http://localhost:3001/api/upload-pdf', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      // Insert data into Excel
      await insertModelIntoExcel(response.data);

      setStatus({ type: 'success', message: 'DCF model created successfully!' });
      onModelCreated();
    } catch (error) {
      console.error('Upload error:', error);
      setStatus({
        type: 'error',
        message: 'Failed to process PDF. Please try again.'
      });
    } finally {
      setUploading(false);
    }
  };

  const insertModelIntoExcel = async (modelData: any) => {
    await Excel.run(async (context) => {
      const sheets = context.workbook.worksheets;

      // Create Assumptions sheet
      let assumptionsSheet = sheets.getItemOrNullObject('Assumptions');
      await context.sync();

      if (assumptionsSheet.isNullObject) {
        assumptionsSheet = sheets.add('Assumptions');
      }

      // Create Financials sheet
      let financialsSheet = sheets.getItemOrNullObject('Financials');
      await context.sync();

      if (financialsSheet.isNullObject) {
        financialsSheet = sheets.add('Financials');
      }

      // Create DCF Calculation sheet
      let dcfSheet = sheets.getItemOrNullObject('DCF Calculation');
      await context.sync();

      if (dcfSheet.isNullObject) {
        dcfSheet = sheets.add('DCF Calculation');
      }

      // Insert assumptions
      if (modelData.assumptions) {
        const assumptionsRange = assumptionsSheet.getRange('A1').getResizedRange(
          modelData.assumptions.length - 1,
          modelData.assumptions[0].length - 1
        );
        assumptionsRange.values = modelData.assumptions;
        assumptionsRange.format.autofitColumns();
      }

      // Insert financial data
      if (modelData.financials) {
        const financialsRange = financialsSheet.getRange('A1').getResizedRange(
          modelData.financials.length - 1,
          modelData.financials[0].length - 1
        );
        financialsRange.values = modelData.financials;
        financialsRange.format.autofitColumns();
      }

      // Insert DCF calculations with formulas
      if (modelData.dcfCalculations) {
        const dcfRange = dcfSheet.getRange('A1').getResizedRange(
          modelData.dcfCalculations.length - 1,
          modelData.dcfCalculations[0].length - 1
        );

        // Set values and formulas
        for (let i = 0; i < modelData.dcfCalculations.length; i++) {
          for (let j = 0; j < modelData.dcfCalculations[i].length; j++) {
            const cell = dcfSheet.getRange(i + 1, j + 1, 1, 1);
            const value = modelData.dcfCalculations[i][j];

            if (typeof value === 'string' && value.startsWith('=')) {
              cell.formulas = [[value]];
            } else {
              cell.values = [[value]];
            }
          }
        }

        dcfSheet.getUsedRange().format.autofitColumns();
      }

      // Format headers
      [assumptionsSheet, financialsSheet, dcfSheet].forEach(sheet => {
        const headerRange = sheet.getRange('1:1');
        headerRange.format.font.bold = true;
        headerRange.format.fill.color = '#667eea';
        headerRange.format.font.color = 'white';
      });

      await context.sync();
    });
  };

  return (
    <div className="upload-container">
      <h2>Upload Company PDF</h2>
      <p style={{ marginBottom: '20px', color: '#666', fontSize: '14px' }}>
        Upload a PDF containing company financial information to automatically generate a DCF model.
      </p>

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
          'Generate DCF Model'
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
