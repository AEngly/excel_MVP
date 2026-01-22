# Excel DCF Model Add-in - AI Agent Instructions

## Project Overview
This is an Excel task pane add-in for private equity and M&A professionals to automate DCF (Discounted Cash Flow) model creation and analysis. The add-in combines PDF data extraction, automated model construction, error checking, and AI-powered financial analysis.

## Core Functionality
1. **PDF Upload & Model Generation**: Extract company data from PDFs, make reasonable assumptions when data is missing (using context + internet research), and insert into formatted Excel tables
2. **Cross-Tab Error Checking**: Validate formulas and values across multiple worksheets in DCF models
3. **Model Chat Interface**: Conversational analysis of DCF models - behavior explanations, conclusions, sensitivity analysis

## Architecture

### Frontend (Excel Task Pane)
- **Technology**: React with Office.js API
- **Location**: `/src/taskpane/` - Contains React components for the UI
- **Entry Point**: Task pane HTML/JS loads React app into Excel side panel
- **Key Pattern**: All Excel interactions use `Office.context.workbook` and async/await patterns
- **State Management**: Keep track of active worksheet, uploaded files, and chat context

### Backend (API Server)
- **Technology**: Python FastAPI with LangChain and OpenAI API
- **Package Manager**: `uv` for fast, reliable dependency management
- **Location**: `/backend/`
- **Responsibilities**:
  - PDF parsing and data extraction (PyPDF2)
  - LLM orchestration for model generation and analysis
  - Formula validation and error detection logic
  - Internet research for missing assumptions

### Excel Integration Patterns
- **Reading Data**: Use `context.workbook.worksheets.getActiveWorksheet()` then `.getRange()` for cell access
- **Writing Data**: Batch operations with `.values` property for performance
- **Cross-Sheet**: Use `.worksheets.getItem(name)` to access different tabs
- **Formulas**: Set via `.formulas` property, validate with `.getFormulas()`

## Development Workflow

### Initial Setup
```bash
# Install Yeoman Office generator (first time only)
npm install -g yo generator-office

# Generate add-in
yo office --projectType taskpane --name "Excel DCF Assistant" --host excel --framework react

# Start development
npm start  # Runs webpack dev server + sideloads into Excel
```

### Backend Development
```bash
cd backend
uv sync  # Install dependencies (creates uv.lock)
uv run python main.py  # Run with auto-reload
```

**Important**: Commit `uv.lock` to ensure reproducible builds across environments.

### Testing
- **Frontend**: Manual testing in Excel Desktop (auto-reloads on save)
- **Backend**: Use Postman/curl for API endpoints
- **E2E**: Test full flow: PDF upload → model creation → error check → chat

## Critical Conventions

### DCF Model Structure
- **Assumptions Sheet**: Store all assumptions (growth rates, WACC, terminal value multiples)
- **Financials Sheet**: Historical + projected income statement, balance sheet, cash flow
- **DCF Calculation Sheet**: Free cash flow calculations, discount factors, valuation output
- **Cross-references**: Use named ranges or structured references for clarity

### LangChain Integration
- **Chain Pattern**: PDF → Extraction → Validation → Excel Instructions → Formatting
- **Context Window**: Keep chat history for model discussion feature
- **Error Handling**: Fallback to default assumptions if LLM fails, log for review

### File Manifest (manifest.xml)
- Located at root or `/manifest.xml`
- Defines add-in entry points, permissions, and UI elements
- Must be updated for production deployment (change localhost to production URL)

## Deployment
- **Frontend**: Serve React build from CDN or static host (must support HTTPS)
- **Backend**: Deploy to cloud service (Azure, AWS, etc.)
- **Sharing**: Users sideload manifest XML or publish to AppSource
- **Environment Variables**: Keep API keys in `.env`, never commit to repo

## Key Files to Reference
- `/frontend/taskpane/components/App.tsx` - Main React component with Excel integration
- `/backend/main.py` - FastAPI app with all API endpoints
- `/backend/pyproject.toml` - Python dependencies (managed by uv)
- `/backend/services/model_service.py` - LLM orchestration for DCF generation
- `/backend/services/chat_service.py` - Conversational AIcessing and model generation
- `/backend/services/langchain.js` - LLM orchestration logic

## Common Pitfalls
- **CORS**: Backend must allow origin from Excel add-in domain
- **Async Excel API**: Always use `context.sync()` after queuing operations
- **Formula Localization**: Formulas may differ by Excel language (use English function names)
- **Large Models**: Batch read/write operations; avoid cell-by-cell loops
