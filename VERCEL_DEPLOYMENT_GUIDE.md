# Vercel Deployment Guide

This guide explains how to deploy the Court Ecosystem application on Vercel with authentication and Google OAuth.

## Architecture Overview

The Court Ecosystem uses a **separated frontend/backend architecture**:

- **Frontend**: Deployed on Vercel (Vanilla HTML/CSS/JavaScript)
- **Backend**: Deployed separately (Python FastAPI)

This separation is necessary because **Vercel natively supports JavaScript/Node.js**, while the backend is built with Python.

## Prerequisites

Before deployment, ensure you have:

- [ ] GitHub account (for Vercel integration)
- [ ] Vercel account (free tier available at vercel.com)
- [ ] Backend server deployed (Heroku, Railway, or your own server)
- [ ] Google OAuth credentials (for Google login)
- [ ] PostgreSQL database (recommended for production)

## Step 1: Google OAuth Setup

### 1.1 Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Enable Google+ API
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Configure consent screen with your app name
6. Select **Web application**
7. Add authorized origins:
   ```
   http://localhost:3000
   https://your-frontend.vercel.app
   ```
8. Add authorized redirect URIs:
   ```
   http://localhost:8000/api/auth/google/callback
   https://your-backend-api.com/api/auth/google/callback
   ```
9. Copy your **Client ID** and **Client Secret**

Save these for later use!

## Step 2: Deploy Backend

### Option A: Deploy to Railway

Railway is recommended for Python backends (free tier available).

1. Push code to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. Go to [railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will detect Python and create backend service
6. Add PostgreSQL plugin:
   - Click "Add Plugins"
   - Select "PostgreSQL"
   - Click "Add"

7. Configure environment variables in Railway:
   ```
   DATABASE_URL=<Railway PostgreSQL URL>
   SECRET_KEY=<generate-a-strong-key>
   GOOGLE_CLIENT_ID=<your-google-client-id>
   GOOGLE_CLIENT_SECRET=<your-google-client-secret>
   ```

8. Deploy and get your backend URL (e.g., `https://your-app.railway.app`)

### Option B: Deploy to Heroku

1. Install Heroku CLI
2. Create Heroku app:
   ```bash
   heroku create your-app-name
   ```
3. Add PostgreSQL addon:
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```
4. Set environment variables:
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set GOOGLE_CLIENT_ID=your-google-client-id
   heroku config:set GOOGLE_CLIENT_SECRET=your-google-client-secret
   ```
5. Deploy:
   ```bash
   git push heroku main
   ```

## Step 3: Prepare Frontend for Vercel

### 3.1 Update Environment Variables

Update `dashboard/login.html` and `dashboard/index.html`:

Replace:
```javascript
const API_BASE_URL = `http://${window.location.hostname}:8000`;
```

With:
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || `http://${window.location.hostname}:8000`;
```

Also update the Google Client ID in `dashboard/login.html`:

Replace:
```html
data-client_id="YOUR_GOOGLE_CLIENT_ID"
```

With your actual Google Client ID.

### 3.2 Create Vercel Configuration

The `vercel.json` file is already created. Ensure it exists in your project root.

## Step 4: Deploy Frontend to Vercel

### 4.1 Connect GitHub to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Sign in with GitHub account
3. Click "Add New..." → "Project"
4. Select your repository
5. Click "Import"

### 4.2 Configure Environment Variables

In Vercel project settings:

1. Go to **Settings** → **Environment Variables**
2. Add the following:

   ```
   REACT_APP_API_URL=https://your-backend-api.com
   REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id
   ```

3. Make sure these are set for all environments (Preview, Production)

### 4.3 Deploy

Vercel will automatically deploy when you push to GitHub:

```bash
git add .
git commit -m "Add authentication and prepare for Vercel deployment"
git push origin main
```

Watch the deployment progress in Vercel dashboard. Once complete, you'll get a live URL like `https://your-project.vercel.app`

## Step 5: Update Google OAuth Callback URL

Update Google Console with your Vercel URLs:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Go to **Credentials** → Select your OAuth app
3. Update **Authorized origins**:
   ```
   https://your-project.vercel.app
   https://www.your-project.vercel.app
   ```
4. Update **Authorized redirect URIs**:
   ```
   https://your-backend-api.com/api/auth/google/callback
   ```

## Step 6: Configure CORS on Backend

Update your backend's CORS configuration:

In `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-project.vercel.app",
        "https://www.your-project.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Testing the Deployment

### 1. Test Backend Endpoints

```bash
# Test API health
curl https://your-backend-api.com/api/dashboard/stats

# Test authentication
curl -X POST https://your-backend-api.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'
```

### 2. Test Frontend

1. Visit `https://your-project.vercel.app`
2. Try email/password login
3. Test Google OAuth login
4. Verify dashboard loads correctly
5. Check browser console for any errors

### 3. Verify JWT Token Storage

1. Open browser DevTools (F12)
2. Go to Application → Local Storage
3. Verify `token` and `user` are saved after login

## Troubleshooting

### CORS Errors

**Error**: "Access to XMLHttpRequest blocked by CORS"

**Solution**: 
- Add your Vercel domain to backend CORS allowed origins
- Check environment variables are set correctly

### Google OAuth Not Working

**Error**: "Invalid Google Client ID" or "Login failed"

**Solution**:
- Verify CLIENT_ID in login.html matches Google Console
- Check authorized origins in Google Console include your Vercel domain
- Ensure GOOGLE_CLIENT_SECRET is set on backend

### Login Always Redirects to Login Page

**Error**: User stays on login.html after login

**Solution**:
- Check if JWT token is being saved to localStorage
- Verify API response includes token field
- Check browser console for errors

### 404 on Dashboard

**Error**: Visiting `/api/cases` returns 404

**Solution**:
- Verify backend API URL is correct in environment variables
- Check backend service is running and accessible
- Verify CORS is properly configured

## Database Migration

For moving from SQLite to PostgreSQL:

```bash
# Export data from SQLite
sqlite3 court_cases.db ".dump" > backup.sql

# Import to PostgreSQL
psql -d your_db_name -f backup.sql
```

## Monitoring & Logs

### Vercel Logs

1. Go to Vercel dashboard
2. Select project
3. Go to **Deployments** or **Logs**
4. Check build and runtime logs

### Backend Logs (Railway/Heroku)

Railway:
- Dashboard → Select service → View logs

Heroku:
```bash
heroku logs --tail
```

## Environment Variables Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `API_BASE_URL` | Backend API endpoint | `https://your-api.railway.app` |
| `SECRET_KEY` | JWT signing secret | `your-secret-key-min-32-chars` |
| `GOOGLE_CLIENT_ID` | Google OAuth Client ID | `xxxxx.apps.googleusercontent.com` |
| `DATABASE_URL` | PostgreSQL connection | `postgresql://user:pass@host/db` |

## Scaling Considerations

- **Database**: PostgreSQL recommended for production
- **Caching**: Consider Redis for session management
- **CDN**: Vercel includes Vercel Edge Network
- **Rate Limiting**: Implement on backend for production
- **Monitoring**: Set up error tracking (Sentry, LogRocket)

## Next Steps

1. Set up database backups
2. Configure automatic scaling
3. Set up monitoring and alerts
4. Enable authentication logging
5. Configure custom domain
6. Set up CI/CD for automated deployments

## Support

For issues or questions:
- Check Vercel documentation: https://vercel.com/docs
- Backend service documentation (Railway/Heroku)
- Google OAuth setup: https://developers.google.com/identity/gsi/web

## Security Checklist

- [ ] SECRET_KEY is strong and unique
- [ ] GOOGLE_CLIENT_SECRET is not exposed
- [ ] CORS is configured for specific domains only
- [ ] Database credentials are secure
- [ ] JWT tokens have expiration
- [ ] HTTPS is enforced
- [ ] Environment variables are not committed to git

---

Happy deploying! 🚀
