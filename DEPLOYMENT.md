# Excel DCF Assistant - Deployment Guide

## For External Users to Test MVP

### Option 1: Quick Deploy (Recommended for MVP)

**Deploy with free hosting services:**

1. **Deploy Frontend (Netlify/Vercel - Free tier)**
   ```bash
   cd frontend
   npm run build
   # Upload dist/ folder to Netlify or connect GitHub repo
   ```

2. **Deploy Backend (Railway/Render - Free tier)**
   ```bash
   # Connect GitHub repo to Railway/Render
   # Set environment variable: OPENAI_API_KEY
   ```

3. **Update manifest.production.xml**
   - Replace `YOUR-DOMAIN.com` with your Netlify/Vercel URL
   - Example: `https://dcf-assistant.netlify.app`

4. **Share with users**
   - Send them `manifest.production.xml`
   - Instructions below

### Option 2: Docker Deploy (Self-hosted)

```bash
# Build production images
docker-compose -f docker-compose.production.yml up -d

# Deploy to your server with Docker support
```

## User Installation Instructions

**How users install your add-in:**

1. Download `manifest.production.xml` from your website/email
2. Open Excel
3. Go to: **Insert** → **Get Add-ins** → **My Add-ins** → **Manage My Add-ins**
4. Click **Upload My Add-in**
5. Select the downloaded `manifest.production.xml`
6. Click **Upload**
7. The add-in appears in the **Home** ribbon → **DCF Tools** section

**First-time use:**
- Click "Show DCF Assistant" button in ribbon
- Task pane opens on the right side with your React UI
- Backend API is called automatically (from hosted URL)

## Deployment Checklist

- [ ] Frontend built: `cd frontend && npm run build`
- [ ] Frontend hosted with HTTPS (Netlify/Vercel/Cloudflare Pages)
- [ ] Backend deployed with OPENAI_API_KEY env var
- [ ] CORS configured to allow frontend domain
- [ ] manifest.production.xml updated with production URLs
- [ ] Icon assets uploaded to hosting
- [ ] Test manifest.xml yourself first
- [ ] Share manifest.production.xml with users

## Quick Deployment Options

### Frontend Hosting (Free)
- **Netlify**: Drag & drop `frontend/dist/` folder
- **Vercel**: Connect GitHub repo, auto-deploy on push
- **Cloudflare Pages**: GitHub integration, fast CDN
- **GitHub Pages**: Works but requires custom domain for HTTPS

### Backend Hosting (Free tier available)
- **Railway**: Connect GitHub, auto-deploy, $5 free credit/month
- **Render**: Free tier (sleeps after inactivity)
- **Fly.io**: Free tier available
- **Heroku**: No longer has free tier
- **Azure/AWS**: Free tier but more complex setup

## Environment Variables for Production

**Backend (.env or hosting platform):**
```
OPENAI_API_KEY=sk-...
PORT=3001
ENVIRONMENT=production
```

**Frontend (build-time):**
```
REACT_APP_API_URL=https://your-backend.railway.app
```

## Update Backend URL in Frontend

Edit `frontend/taskpane/components/PdfUpload.tsx`, `ErrorChecker.tsx`, `ModelChat.tsx`:

```typescript
// Change from:
axios.post('http://localhost:3001/api/upload-pdf', ...)

// To:
axios.post('https://your-backend.railway.app/api/upload-pdf', ...)
```

Or use environment variable:
```typescript
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001';
axios.post(`${API_URL}/api/upload-pdf`, ...)
```
