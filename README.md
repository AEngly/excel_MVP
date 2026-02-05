# Excel DCF Assistant

AI-powered Excel add-in for automating DCF (Discounted Cash Flow) model creation and analysis. Built for private equity and M&A professionals.

## Features

1. **📄 PDF Upload & Model Generation** - Upload company PDFs (financial statements, presentations) and automatically generate complete DCF models
2. **✓ Cross-Tab Error Checking** - Validate formulas and values across multiple worksheets
3. **💬 Model Chat Interface** - Ask questions, run sensitivity analysis, and understand model behavior

## Tech Stack

- **Frontend**: React + Office.js (Excel Task Pane Add-in)
- **Backend**: Python FastAPI + LangChain + OpenAI (managed with `uv`)
- **AI**: GPT-4 for model generation and analysis

## Project Structure

```
excel_MVP/
├── frontend/           # React task pane UI
│   ├── taskpane/      # Main task pane components
│   └── commands/      # Office commands
├── backend/           # Python FastAPI backend
│   ├── main.py        # FastAPI app
│   └── services/      # Business logic (PDF, model gen, chat)
├── manifest.xml       # Excel add-in manifest
└── webpack.config.js  # Frontend build config
```

## Setup Instructions

### Prerequisites

- Node.js 16+ and npm
- Python 3.9+
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Excel (Desktop or Online)
- OpenAI API key

### 1. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 2. Setup Backend

```bash
cd backend

# Install dependencies with uv (creates .venv and uv.lock automatically)
uv sync

# Create .env file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

> **Note**: `uv sync` creates a lockfile (`uv.lock`) for reproducible builds. Commit this file to version control.

### 3. Run Development Servers

**Terminal 1 - Frontend (Excel Add-in):**
```bash
cd frontend
npm start
# This starts webpack dev server and sideloads the add-in into Excel
```

**Terminal 2 - Backend API:**
```bash
cd backend
uv run python main.py
# Or if already in uv environment:
python main.py
# Server runs on http://localhost:3001
```

### 4. Docker Option (Alternative)

```bash
# Build and run with Docker Compose
docker-compose up

# Frontend: http://localhost:3000
# Backend: http://localhost:3001
```

### 4. Load Add-in in Excel

The `npm start` command automatically sideloads the add-in. If needed manually:

1. Open Excel
2. Go to Insert > My Add-ins > Manage My Add-ins
3. Upload `manifest.xml`
4. Click "Show Taskpane" from the ribbon

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


