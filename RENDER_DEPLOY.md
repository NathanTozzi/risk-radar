# Render Deployment Guide

This monorepo contains a React/Vite frontend and FastAPI backend, configured for deployment on Render.

## Architecture

- **Frontend**: React + TypeScript + Vite → Static Site
- **Backend**: FastAPI + Python 3.11 → Web Service (Docker)
- **Configuration**: `render.yaml` for monorepo deployment

## Local Verification

Before deploying, verify both services work locally:

### Frontend Build Test
```bash
cd frontend
npm ci
npm run build
test -d dist && echo "✅ Frontend build successful" || echo "❌ Build failed"
cd ..
```

### Backend Docker Test  
```bash
cd backend
docker build -t risk-radar-backend:test .
docker run -d --name test-backend -p 8001:8000 -e PORT=8000 risk-radar-backend:test
curl http://localhost:8001/health
# Should return: {"status":"healthy","service":"RiskRadar"}
docker rm -f test-backend
cd ..
```

## Deployment Process

1. **Push to main branch** - Render auto-deploys from `render.yaml`
2. **Frontend service** builds in `/frontend` and publishes `/frontend/dist`  
3. **Backend service** builds Docker image from `/backend/Dockerfile`
4. **Services connect** via Render's internal networking

## Troubleshooting

### "Publish directory dist does not exist"
- ✅ **Fixed**: `render.yaml` now uses `rootDir: frontend` and proper build commands
- The build runs in `/frontend` and creates `/frontend/dist`

### Backend port issues
- ✅ **Fixed**: Dockerfile uses `$PORT` environment variable (Render requirement)
- Health check endpoint: `/health`

### Build failures
- Frontend uses lenient TypeScript config to prevent build failures
- Dependencies are properly declared in `package.json`

## Services URLs (after deployment)

- **Frontend**: `https://risk-radar-frontend.onrender.com`  
- **Backend**: `https://risk-radar-backend.onrender.com`
- **API Docs**: `https://risk-radar-backend.onrender.com/docs`

## Manual Deployment Steps (if needed)

1. Create Static Site service in Render dashboard
2. Point to this repository  
3. Use these settings:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm ci && npm run build`
   - **Publish Directory**: `dist`

4. Create Web Service for backend
5. Use these settings:
   - **Root Directory**: `backend` 
   - **Environment**: Docker
   - **Dockerfile Path**: `Dockerfile`