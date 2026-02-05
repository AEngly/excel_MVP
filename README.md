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

## Usage

1. **Upload PDF**: Click "Upload PDF" tab, select a company PDF, and click "Generate DCF Model"
2. **Check Errors**: Once model is created, use "Check Errors" to validate formulas
3. **Chat**: Ask questions like "What's the enterprise value?" or "How would 15% growth affect valuation?"

## Development

### Frontend Development
- React components in `frontend/taskpane/components/`
- Edit `App.tsx`, `PdfUpload.tsx`, `ErrorChecker.tsx`, `ModelChat.tsx`
- Webpack auto-reloads on save

### Backend Development
- Python services in `backend/services/`
- `model_service.py` - DCF generation logic
- `error_check_service.py` - Validation logic
- `chat_service.py` - Conversational AI
- FastAPI auto-reloads with `uvicorn --reload`

## Deployment

**For External Users / MVP Testing:**

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

**Quick summary:**
1. Deploy frontend to Netlify/Vercel (free)
2. Deploy backend to Railway/Render (free tier)
3. Update `manifest.production.xml` with your deployed URLs
4. Share manifest file with users - they sideload it in Excel

**Frontend**: Build and host static files
```bash
npm run build
# Deploy dist/ to CDN/static host (must be HTTPS)
# Update manifest.xml URLs from localhost to production
```

**Backend**: Deploy Python app
```bash
# Deploy to cloud (Heroku, AWS, Azure, etc.)
# Set OPENAI_API_KEY environment variable
```

## Troubleshooting

- **CORS errors**: Ensure backend allows `https://localhost:3000` origin
- **Add-in not loading**: Clear Office cache, restart Excel
- **API errors**: Check `.env` has valid `OPENAI_API_KEY`

## License

MIT

The purpose is to use the data in the files to establish DCF models used in private equity and M&A. If assumptions cannot be established from the file, they should be made based on context of the file and internet searches. The data should be inserted in nicely formatted tables (if existing ones do not exist already)

2) Check for errors in the DCF model

Check formulas and numbers to make sure everything is "right". Remember we have to work across tabs.

3) General chat with the constructed models - why do they behave the way the do, and what could be conclusions? How would certain assumptions affect the result?

I need an MVP as fast as possible. It should be an Excel plug-in in the pane. I need it in a way where we can share the plug-in and the backend (with LangChain and OpenAI/similar API calls are handled as well as formatting of the instructions to create the models in Excel). Let's start by getting something up in the pane. Create it in React according to best practices.


