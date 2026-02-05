# Docker Deployment Guide

## Deployment Options with Docker

### Option 1: Railway (Easiest - Full Docker Support)
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Deploy backend
cd backend
railway up
# Get backend URL: https://xxx.up.railway.app

# Deploy frontend
cd ../frontend
# Build with backend URL
docker build --build-arg REACT_APP_API_URL=https://xxx.up.railway.app -t dcf-frontend .
railway up
# Get frontend URL: https://yyy.up.railway.app
```

### Option 2: Google Cloud Run (Serverless Containers)
```bash
# Backend
cd backend
gcloud run deploy dcf-backend \
  --source . \
  --set-env-vars OPENAI_API_KEY=sk-xxx \
  --allow-unauthenticated

# Frontend
cd ../frontend
gcloud run deploy dcf-frontend \
  --source . \
  --set-env-vars REACT_APP_API_URL=https://dcf-backend-xxx.run.app \
  --allow-unauthenticated
```

### Option 3: AWS ECS / Azure Container Apps
Deploy using their Docker container services - similar process.

### Option 4: Self-Hosted Server (DigitalOcean, Linode, etc.)
```bash
# SSH into your server
ssh user@your-server.com

# Install Docker & Docker Compose
curl -fsSL https://get.docker.com | sh

# Clone your repo
git clone https://github.com/your-repo/excel_MVP.git
cd excel_MVP

# Create .env file
echo "OPENAI_API_KEY=sk-your-key" > .env
echo "REACT_APP_API_URL=https://your-server.com" >> .env

# Deploy with docker-compose
docker-compose -f docker-compose.production.yml up -d

# Setup nginx reverse proxy (optional - for custom domain)
```

## Complete Deployment Flow

**1. Build and test locally:**
```bash
cd /Users/andreasengly/Documents/GitHub/excel_MVP
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up
```

**2. Deploy to cloud** (choose Railway for simplicity):
```bash
railway login
cd backend && railway up
cd ../frontend && railway up
```

**3. Get deployment URLs:**
- Frontend: `https://dcf-frontend-xxx.up.railway.app`
- Backend: `https://dcf-backend-xxx.up.railway.app`

**4. Update manifest.production.xml:**
- Replace `YOUR-DOMAIN.com` with `dcf-frontend-xxx.up.railway.app`

**5. Share manifest.production.xml:**
- Users download it
- Sideload in Excel
- Done! ✅

## Benefits of Docker Deployment

✅ **Reproducible** - Same environment everywhere
✅ **Isolated** - No dependency conflicts
✅ **Scalable** - Easy to scale up/down
✅ **Portable** - Deploy anywhere (AWS, GCP, Azure, Railway, etc.)
✅ **Fast** - Pre-built images deploy in seconds
✅ **Reliable** - Container health checks and auto-restart

## Cost Estimate (Monthly)

- **Railway**: Free tier → $5-10 for hobby usage
- **Google Cloud Run**: Pay-per-use, ~$5-20
- **DigitalOcean Droplet**: $6-12 (cheapest self-hosted)
- **Netlify (frontend only)**: Free tier available
