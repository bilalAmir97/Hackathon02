# Hugging Face Spaces Deployment Guide

## Prerequisites
- Hugging Face account (https://huggingface.co)
- Git installed locally

## Deployment Steps

### Option 1: Deploy via Hugging Face Web Interface (Easiest)

1. **Create a new Space**
   - Go to https://huggingface.co/new-space
   - Space name: `hackathon02-backend`
   - License: MIT
   - SDK: Docker
   - Click "Create Space"

2. **Clone the Space repository**
   ```bash
   git clone https://huggingface.co/spaces/YOUR_USERNAME/hackathon02-backend
   cd hackathon02-backend
   ```

3. **Copy backend files to the Space**
   ```bash
   # From your project root
   cp -r Phase-II/backend/* hackathon02-backend/
   ```

4. **Configure Environment Variables**
   - Go to your Space settings on Hugging Face
   - Add these secrets:
     ```
     DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_5WXqtjQ8BTJG@ep-morning-dream-ahd6dj34-pooler.c-3.us-east-1.aws.neon.tech/neondb
     JWT_SECRET=dcVvHdtoVo7WdWJckczaReV3xcyR5Co1
     FRONTEND_URL=https://frontend-puce-chi-82.vercel.app
     CORS_ALLOW_CREDENTIALS=true
     APP_ENV=production
     LOG_LEVEL=INFO
     ```

5. **Push to Hugging Face**
   ```bash
   cd hackathon02-backend
   git add .
   git commit -m "Initial backend deployment"
   git push
   ```

6. **Wait for build**
   - Hugging Face will automatically build and deploy your Docker container
   - Your API will be available at: `https://YOUR_USERNAME-hackathon02-backend.hf.space`

### Option 2: Deploy via Git (Direct Push)

1. **Authenticate with Hugging Face**
   ```bash
   # You'll need to run this in your local terminal
   huggingface-cli login
   ```

2. **Create Space and push**
   ```bash
   cd Phase-II/backend
   git init
   git remote add space https://huggingface.co/spaces/YOUR_USERNAME/hackathon02-backend
   git add .
   git commit -m "Initial backend deployment"
   git push space main
   ```

## After Deployment

1. **Get your backend URL**
   - Format: `https://YOUR_USERNAME-hackathon02-backend.hf.space`

2. **Update Frontend Environment Variables**
   - Go to Vercel Dashboard → Your Project → Settings → Environment Variables
   - Update `NEXT_PUBLIC_API_URL` to your HF Space URL
   - Redeploy frontend: `vercel --prod`

3. **Test your API**
   ```bash
   curl https://YOUR_USERNAME-hackathon02-backend.hf.space/health
   ```

## Troubleshooting

### Build Failures
- Check build logs in HF Spaces dashboard
- Verify Dockerfile is correct
- Ensure all dependencies in requirements.txt are available

### Database Connection Issues
- Verify DATABASE_URL secret is set correctly
- Check Neon database allows connections from HF Spaces IPs
- Ensure connection string uses `postgresql+asyncpg://` prefix

### CORS Errors
- Verify FRONTEND_URL matches your Vercel deployment
- Check CORS_ALLOW_CREDENTIALS is set to `true`

## Notes

- Hugging Face Spaces provides free hosting with some limitations
- Your Space will sleep after inactivity (cold starts may occur)
- For production, consider upgrading to a paid tier for better performance
