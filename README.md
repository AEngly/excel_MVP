# Excel DCF Assistant

AI-powered Excel add-in for automating DCF (Discounted Cash Flow) model creation and analysis. Built for private equity and M&A professionals.

## Features

1. **📄 PDF Upload & Model Generation** - Upload company PDFs (financial statements, presentations) and automatically generate complete DCF models with AI-powered data extraction and reasonable assumptions
2. **✓ Cross-Tab Error Checking** - Validate formulas and values across multiple worksheets in DCF models
3. **💬 Model Chat Interface** - Conversational analysis with agent mode (read-only chat or write-enabled actions), sensitivity analysis, and model behavior explanations
4. **📚 Session Management** - Track uploaded PDFs with embeddings for contextual retrieval across chat sessions

## Tech Stack

- **Frontend**: React 18 + TypeScript + Office.js API
- **Backend**: Python 3.9+ with FastAPI + LangChain + OpenAI
- **Package Management**: `uv` (Python) and `npm` (Node.js)
- **Deployment**: Docker + Docker Compose with nginx
- **AI**: GPT-4 for intelligent model generation, error checking, and conversational analysis

## Project Structure

```
excel_MVP/
├── frontend/                    # React task pane add-in
│   ├── taskpane/
│   │   ├── components/
│   │   │   ├── App.tsx         # Main app with tab navigation
│   │   │   ├── PdfUpload.tsx   # PDF upload + model generation
│   │   │   ├── ErrorChecker.tsx # Error validation UI
│   │   │   └── ModelChat.tsx   # Chat interface with agent mode
│   │   ├── config.ts           # API_BASE_URL configuration
│   │   └── index.tsx           # React entry point
│   ├── commands/               # Office ribbon commands
│   ├── package.json
│   ├── webpack.config.js       # Dev server + build config
│   └── Dockerfile
├── backend/                     # Python FastAPI backend
│   ├── main.py                 # FastAPI app with CORS
│   ├── pyproject.toml          # Dependencies (managed by uv)
│   ├── services/
│   │   ├── pdf_service.py      # PDF text extraction (PyPDF2)
│   │   ├── model_service.py    # DCF generation with LangChain
│   │   ├── error_check_service.py # Formula validation
│   │   ├── chat_service.py     # Conversational AI
│   │   ├── embedding_service.py # Vector embeddings for PDFs
│   │   ├── session_service.py  # Session tracking
│   │   ├── summary_service.py  # PDF summarization
│   │   └── action_validator.py # Validate Excel actions
│   └── Dockerfile
├── nginx/
│   └── nginx.conf              # Reverse proxy config
├── manifest.xml                # Development manifest (localhost:3000)
├── manifest.production.xml     # Production manifest template
├── manifest.docker.xml         # Docker deployment manifest
├── docker-compose.yml          # Development with Docker
├── docker-compose.production.yml # Production Docker setup
├── DEPLOYMENT.md               # Deployment guide (cloud/free hosting)
└── DEPLOYMENT_DOCKER.md        # Docker deployment guide
```

## Quick Start Guide

### Prerequisites

- **Node.js** 16+ and npm
- **Python** 3.9 or higher
- **uv** - Fast Python package manager ([Install guide](https://github.com/astral-sh/uv))
  ```bash
  # macOS/Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh

  # Windows PowerShell
  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- **Excel** (Desktop for Windows/Mac or Excel Online)
- **OpenAI API Key** - Get from [OpenAI Platform](https://platform.openai.com/api-keys)

### Option 1: Local Development (Recommended for Development)

**Step 1: Clone and Setup**
```bash
git clone <your-repo-url>
cd excel_MVP
```

**Step 2: Backend Setup**
```bash
cd backend

# Install dependencies with uv (auto-creates .venv and uv.lock)
uv sync

# Create environment file
echo "OPENAI_API_KEY=your-openai-api-key-here" > .env

# Verify installation
uv run python -c "import fastapi; print('✅ Backend ready')"
```

**Step 3: Frontend Setup**
```bash
cd ../frontend

# Install dependencies
npm install

# Verify installation
npm run validate  # Validates manifest.xml
```

**Step 4: Start Development Servers**

Open **two terminals**:

**Terminal 1 - Backend:**
```bash
cd backend
uv run python main.py
# Server starts on http://localhost:3001
# You should see: "Uvicorn running on http://0.0.0.0:3001"
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
# Webpack dev server starts on https://localhost:3000
# Excel add-in automatically sideloads into Excel Desktop
```

**What happens:**
- Frontend dev server starts with hot reload
- Self-signed SSL certificate generated (required by Office.js)
- Excel opens automatically with the add-in loaded
- Task pane appears on the right side of Excel

**Step 5: Using the Add-in**

The add-in should appear automatically in Excel. If not:

1. Open Excel
2. Go to **Home** tab → **Add-ins** section
3. Click **Show Taskpane** (or your ribbon button)
4. The DCF Assistant pane opens on the right

### Option 2: Docker (Recommended for Testing/Production-like Environment)

**Step 1: Install Docker**
- Download from [docker.com](https://www.docker.com/get-started)

**Step 2: Create Environment File**
```bash
cd excel_MVP
echo "OPENAI_API_KEY=your-openai-api-key-here" > .env
```

**Step 3: Start with Docker Compose**
```bash
# Development mode (with hot reload)
docker-compose up

# Production mode (optimized builds)
docker-compose -f docker-compose.production.yml up -d
```

**Services:**
- Frontend: http://localhost:3000
- Backend: http://localhost:3001

**Step 4: Sideload Manifest**

Since Excel runs outside Docker, manually sideload:

1. Open Excel
2. **Insert** → **Get Add-ins** → **My Add-ins** → **Manage My Add-ins**
3. Click **Upload My Add-in**
4. Select `/excel_MVP/manifest.xml` (for development) or `manifest.docker.xml` (for Docker)
5. Click **Upload**
6. Click the ribbon button to show the task pane

## How to Use the Add-in

### 1. Upload PDF & Generate DCF Model

**In Excel task pane:**
1. Click **📄 Upload PDF** tab
2. Click **Choose File** and select a company PDF (financial statements, investor deck, etc.)
3. Click **Upload & Generate Model**
4. Wait 30-60 seconds while AI:
   - Extracts financial data from PDF
   - Makes reasonable assumptions for missing data (using context + internet research)
   - Generates DCF model structure in Excel
   - Creates formatted tables across multiple worksheets

**What gets created:**
- **Assumptions** sheet: Growth rates, WACC, terminal value assumptions
- **Financials** sheet: Historical and projected income statement, balance sheet, cash flows
- **DCF** sheet: Free cash flow calculations, discounting, valuation output

### 2. Check for Errors

**After model is created:**
1. Switch to **✓ Check Errors** tab
2. Click **Run Error Check**
3. AI validates:
   - Formula correctness across worksheets
   - Circular references
   - Inconsistent assumptions
   - Missing data
   - Mathematical errors

**Results:**
- Green ✅: No errors found
- Red ❌: Errors detected with specific locations and explanations
- Warnings ⚠️: Potential issues to review

### 3. Chat with Your Model

**Two modes available:**

**A) Read-Only Chat (Safe Mode):**
1. Switch to **💬 Chat** tab
2. Ensure **Agent Mode** toggle is OFF
3. Ask questions like:
   - "What is the enterprise value?"
   - "How sensitive is the valuation to WACC?"
   - "Explain the revenue growth assumptions"
   - "What happens if we increase growth by 5%?"
4. AI analyzes the model and explains behavior without making changes

**B) Agent Mode (Write-Enabled):**
1. Toggle **Agent Mode** ON
2. Give instructions to modify the model:
   - "Increase revenue growth to 15%"
   - "Change WACC to 10%"
   - "Add a sensitivity table for terminal growth rates"
   - "Create a scenario analysis comparing 3 growth rates"
3. AI validates actions, then executes Excel writes

**Session Context:**
- All uploaded PDFs are tracked with vector embeddings
- Chat can reference data from multiple PDFs
- Session history maintained for context-aware conversations

### 4. Uploaded Sessions Panel

**At the bottom of Upload tab:**
- View all uploaded PDF sessions
- See filename, upload time, chunk count
- Read AI-generated summary of each PDF
- Click **🗑️** to remove a session from context

## Development Guide

### Frontend Architecture

**Location:** `/frontend/taskpane/components/`

**Key Components:**
- **App.tsx** - Main container with tab navigation, backend health check, session management
- **PdfUpload.tsx** - File upload, model generation trigger, session display
- **ErrorChecker.tsx** - Error validation UI, results display
- **ModelChat.tsx** - Chat interface with agent mode toggle, message history

**Configuration:**
- `config.ts` - Set `API_BASE_URL` (default: `http://localhost:3001`)
- Webpack dev server runs on `https://localhost:3000` with hot reload

**Excel Integration Pattern:**
```typescript
await Excel.run(async (context) => {
  const sheet = context.workbook.worksheets.getActiveWorksheet();
  const range = sheet.getRange("A1:C10");
  range.load("values");
  await context.sync();

  // Modify values
  range.values = newData;
  await context.sync();
});
```

**Making Changes:**
1. Edit components in `frontend/taskpane/components/`
2. Webpack auto-reloads in Excel (no manual refresh needed)
3. Check browser DevTools (F12 in task pane)
4. Validate manifest: `npm run validate`

### Backend Architecture

**Location:** `/backend/`

**API Endpoints (main.py):**
```python
POST /upload-pdf          # Upload PDF, extract text, create embeddings
POST /generate-model      # Generate DCF model from PDF data
POST /check-errors        # Validate model for errors
POST /chat                # Chat with model (read-only or agent mode)
GET  /health              # Health check endpoint
GET  /session/{id}        # Retrieve session data
```

**Services:**

1. **pdf_service.py** - PyPDF2 text extraction
   ```python
   def extract_text_from_pdf(file_bytes: bytes) -> str
   ```

2. **model_service.py** - LangChain DCF generation
   ```python
   def generate_dcf_model(pdf_text: str) -> dict
   # Returns Excel instructions as JSON
   ```

3. **error_check_service.py** - Formula validation
   ```python
   def check_model_errors(model_data: dict) -> dict
   # Cross-tab error checking logic
   ```

4. **chat_service.py** - Conversational AI
   ```python
   def chat_with_model(message: str, model_data: dict, history: list, agent_mode: bool) -> dict
   # Agent mode determines if Excel writes are allowed
   ```

5. **embedding_service.py** - Vector embeddings for semantic search
   ```python
   def process_pdf_for_search(text: str, session_id: str) -> dict
   ```

6. **session_service.py** - Session tracking
7. **summary_service.py** - PDF summarization
8. **action_validator.py** - Validate Excel actions before execution

**Development Workflow:**
```bash
cd backend

# Start dev server with auto-reload
uv run python main.py

# Or activate virtual environment first
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
python main.py

# Run tests
uv run python test_services.py
```

**Adding Dependencies:**
```bash
# Add package
uv add package-name

# This updates pyproject.toml and uv.lock
# Commit both files
```

### Environment Variables

**Backend (.env file):**
```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx  # Required
PORT=3001                               # Optional, default 3001
ENVIRONMENT=development                 # Optional
```

**Frontend (config.ts):**
```typescript
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001';
```

For production builds, set `REACT_APP_API_URL` before `npm run build`.

### Testing

**Manual Testing:**
1. Use Excel Desktop for full Office.js API testing
2. Check console logs in task pane (F12)
3. Monitor backend logs in terminal
4. Test all three tabs (Upload, Errors, Chat)

**Backend API Testing:**
```bash
# Use curl or Postman
curl http://localhost:3001/health

# Test PDF upload
curl -X POST http://localhost:3001/upload-pdf \
  -F "file=@test_data/sample_company.txt"
```

**Test Data:**
- `backend/test_data/sample_company.txt` - Sample company data
- `backend/test_data/sample_model.json` - Sample DCF model structure
- `backend/test_data/model_with_errors.json` - Model with intentional errors

### Debugging

**Frontend Issues:**
- Open DevTools in task pane (F12 or right-click → Inspect)
- Check Network tab for API calls
- Verify CORS headers in responses
- Clear Office cache: `npx office-addin-dev-settings clear-cache`

**Backend Issues:**
- Check terminal for FastAPI logs
- Verify `.env` file exists with valid API key
- Test endpoint directly with curl/Postman
- Enable debug logging:
  ```python
  import logging
  logging.basicConfig(level=logging.DEBUG)
  ```

**CORS Errors:**
- Backend must allow `https://localhost:3000` (dev) or your production URL
- Check `main.py` CORS middleware configuration:
  ```python
  allow_origins=["https://localhost:3000", "http://localhost:3000"]
  ```

## Deployment

For detailed deployment instructions, see:
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deploy to free cloud services (Netlify, Railway, Render)
- **[DEPLOYMENT_DOCKER.md](DEPLOYMENT_DOCKER.md)** - Docker deployment to Railway, GCP, AWS, etc.

### Quick Deployment Summary

**Option 1: Free Cloud Hosting (Easiest for MVP)**

1. **Frontend** (Netlify/Vercel/Cloudflare Pages):
   ```bash
   cd frontend
   npm run build
   # Upload dist/ folder to hosting service
   ```

2. **Backend** (Railway/Render):
   - Connect GitHub repo
   - Set environment variable: `OPENAI_API_KEY=sk-...`
   - Auto-deploy on push

3. **Update Manifest:**
   - Edit `manifest.production.xml`
   - Replace `YOUR-DOMAIN.com` with your frontend URL
   - Example: `https://dcf-assistant.netlify.app`

4. **Share with Users:**
   - Send them `manifest.production.xml`
   - Users sideload in Excel: **Insert** → **Get Add-ins** → **Upload My Add-in**

**Option 2: Docker Deployment**

```bash
# Local testing
docker-compose -f docker-compose.production.yml up -d

# Deploy to Railway
railway up  # From both frontend/ and backend/ directories

# Deploy to Google Cloud Run
gcloud run deploy --source . --allow-unauthenticated
```

**Option 3: Self-Hosted Server**

```bash
# SSH into server with Docker installed
git clone <your-repo>
cd excel_MVP

echo "OPENAI_API_KEY=sk-..." > .env
docker-compose -f docker-compose.production.yml up -d

# Setup nginx reverse proxy for custom domain
# Use manifest.production.xml with your domain
```

### Important Notes

- **HTTPS Required:** Excel add-ins require HTTPS (except localhost)
- **CORS:** Backend must allow frontend domain in CORS settings
- **API Key:** Set `OPENAI_API_KEY` as environment variable, never commit to repo
- **Manifest Files:**
  - `manifest.xml` - Local development (localhost:3000)
  - `manifest.docker.xml` - Docker deployment
  - `manifest.production.xml` - Cloud production deployment

### User Installation (End Users)

**How users add your deployed add-in:**

1. Download `manifest.production.xml` from your website/email
2. Open Excel
3. **Insert** → **Get Add-ins** → **My Add-ins** (top-left dropdown)
4. Click **Manage My Add-ins** (gear icon bottom-right)
5. Click **Upload My Add-in**
6. Select downloaded manifest file
7. Click **Upload**
8. Ribbon button appears → Click to open task pane

**No installation or admin rights required!**

## Troubleshooting

### Common Issues

**1. Add-in doesn't load in Excel**
```bash
# Clear Office cache
npx office-addin-dev-settings clear-cache

# Restart Excel completely
# Verify manifest.xml is valid
cd frontend
npm run validate
```

**2. Backend CORS errors in browser console**
- Check `backend/main.py` allows your frontend URL:
  ```python
  allow_origins=["https://localhost:3000", "http://localhost:3000", "YOUR_PRODUCTION_URL"]
  ```
- Restart backend after changes: `uv run python main.py`

**3. "Backend: 🔴 Offline" in task pane**
```bash
# Test backend directly
curl http://localhost:3001/health

# Check backend is running
cd backend
uv run python main.py

# Verify no firewall blocking port 3001
# Check backend URL in frontend/taskpane/config.ts
```

**4. OpenAI API errors**
```bash
# Verify API key is set
cd backend
cat .env  # Should show OPENAI_API_KEY=sk-...

# Test API key
uv run python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"

# Check API key is valid at https://platform.openai.com/api-keys
# Ensure you have credits available
```

**5. "npm start" fails with certificate error**
```bash
# Regenerate dev certificates
cd frontend
npx office-addin-dev-certs install

# macOS: May need to trust certificate in Keychain Access
# Windows: May need admin rights
```

**6. Docker container won't start**
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Verify .env file exists
ls -la .env

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up
```

**7. Model generation fails or produces errors**
- Check PDF file isn't corrupted
- Verify PDF contains actual text (not just scanned images)
- Check backend logs for LangChain errors
- Ensure sufficient OpenAI API credits
- Try with `backend/test_data/sample_company.txt` as test

**8. Excel API "GeneralException" errors**
- Ensure Excel file is saved (add-in needs WriteDocument permission)
- Check Office.js API compatibility (use Excel Desktop, not Online for development)
- Verify async/await patterns in code
- Check for missing `context.sync()` calls

**9. Changes not appearing in Excel**
```bash
# Frontend hot reload sometimes fails
# Manually refresh: File → Options → Add-ins → Manage Add-ins → Refresh

# Or restart completely
npm run stop
npm start
```

**10. Port already in use**
```bash
# Find process using port 3000 or 3001
lsof -i :3000  # macOS/Linux
netstat -ano | findstr :3000  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

### Getting Help

**Check logs in order:**
1. Frontend browser console (F12 in task pane)
2. Webpack dev server terminal
3. Backend FastAPI terminal
4. Docker logs (if using Docker)

**Debugging checklist:**
- [ ] Backend running on port 3001
- [ ] Frontend running on port 3000
- [ ] `.env` file exists with valid OpenAI key
- [ ] CORS allows frontend URL
- [ ] Manifest.xml points to correct URLs
- [ ] Office cache cleared if behavior is stale
- [ ] Excel file is saved (for WriteDocument permission)

### Performance Tips

**Large PDFs:**
- PDFs over 50 pages may take 60-90 seconds
- Consider splitting into smaller files
- Monitor OpenAI API usage and costs

**Model generation:**
- First generation takes longer (LLM planning)
- Subsequent chats are faster (cached context)
- Agent mode with writes is slower than read-only

**Excel performance:**
- Batch Excel operations instead of cell-by-cell
- Use `context.sync()` only when necessary
- Avoid reading/writing large ranges repeatedly

## Architecture Notes

### How It Works

1. **PDF Upload Flow:**
   - User uploads PDF in task pane
   - Frontend sends file to backend `/upload-pdf`
   - Backend extracts text with PyPDF2
   - Text chunked and embedded with OpenAI embeddings
   - Session created with unique ID
   - Summary generated with LLM

2. **Model Generation Flow:**
   - User clicks "Generate DCF Model"
   - Frontend sends session ID to `/generate-model`
   - Backend retrieves PDF text from session
   - LangChain orchestrates LLM to:
     - Extract financial data
     - Make assumptions for missing data (with internet research)
     - Generate Excel instructions (JSON format)
   - Frontend receives JSON instructions
   - Office.js executes Excel writes (create sheets, formulas, formatting)

3. **Error Checking Flow:**
   - User clicks "Run Error Check"
   - Frontend reads all worksheets with Office.js
   - Sends model data to `/check-errors`
   - Backend validates:
     - Formula syntax
     - Cross-sheet references
     - Circular dependencies
     - Assumption consistency
   - Returns error list with locations

4. **Chat Flow (Read-Only):**
   - User types question
   - Frontend sends message + model data + session IDs to `/chat`
   - Backend retrieves relevant PDF chunks with embeddings
   - LLM analyzes question with context
   - Returns natural language response

5. **Chat Flow (Agent Mode):**
   - Same as read-only, but `agentMode: true`
   - LLM generates Excel action instructions
   - Backend validates actions with `action_validator`
   - Frontend receives actions
   - Office.js executes Excel writes
   - Confirmation sent to user

### Security Considerations

- **API Key:** Never commit `.env` to git (in `.gitignore`)
- **User Data:** PDFs processed in-memory, not permanently stored
- **Sessions:** Stored in-memory only (lost on server restart)
- **Excel Permissions:** Add-in requests `ReadWriteDocument` permission
- **CORS:** Whitelist only your frontend domains
- **HTTPS:** Required for production (Office.js requirement)

### Key Dependencies

**Frontend:**
- `office-js` - Excel API integration
- `react` - UI framework
- `axios` - HTTP requests to backend
- `webpack` - Dev server with hot reload

**Backend:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `langchain` - LLM orchestration
- `openai` - GPT-4 API client
- `pypdf2` - PDF text extraction
- `python-dotenv` - Environment variables

## License

MIT License - See [LICENSE](LICENSE) for details

## Contributing

Pull requests welcome! Please:
1. Fork the repo
2. Create a feature branch
3. Make changes with clear commit messages
4. Test thoroughly (frontend + backend)
5. Update README if adding features
6. Submit PR with description

## Support

For issues:
1. Check [Troubleshooting](#troubleshooting) section
2. Search existing GitHub issues
3. Create new issue with:
   - Steps to reproduce
   - Error messages
   - Environment (OS, Excel version, Node/Python versions)
   - Logs (frontend console + backend terminal)

---

**Built for private equity and M&A professionals to accelerate DCF modeling with AI.**


