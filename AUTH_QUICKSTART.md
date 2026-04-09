# Quick Start - After Adding Authentication

Follow these steps to run the application locally with the new authentication system.

## Prerequisites

Ensure you have:
- Python 3.9+
- Git
- All required packages installed

## Step 1: Install New Dependencies

```bash
cd /Volumes/PortableSSD/court-ecosystem
pip install -r backend/requirements.txt
```

This installs:
- `PyJWT` - JWT token generation and verification
- `google-auth` - Google OAuth support
- `python-jose` - Additional security utilities

## Step 2: Update Environment Variables

Edit `backend/.env` or create `.env` in project root:

```bash
# Authentication
SECRET_KEY=your-secret-key-change-this-in-production
GOOGLE_CLIENT_ID=your-google-client-id

# Database (already configured)
DATABASE_URL=sqlite:////Volumes/PortableSSD/court-ecosystem/data/court_ecosystem.db
```

## Step 3: Start the Backend Server

From the project root:

```bash
cd backend
PYTHONPATH=/Volumes/PortableSSD/court-ecosystem/backend \
python3 -m uvicorn app.main:app --host localhost --port 8000
```

You should see:
```
✅ User table initialized
📊 Application startup complete
Uvicorn running on http://localhost:8000
```

## Step 4: Access the Application

1. **Login Page**: Open `dashboard/login.html` in your browser or
   ```
   http://localhost:8000/dashboard/login.html
   ```

2. **Demo Credentials** (auto-create on first login):
   - Email: `test@example.com`
   - Password: `password123`

3. **After Login**: You'll be redirected to the main dashboard

## Step 5: Test Features

### Email/Password Login
1. Go to login page
2. Enter any email and password
3. Click "Sign In"
4. First login creates user account automatically

### Google OAuth (Optional)
Only works if you have:
1. Google Client ID configured
2. Your website added to Google Console authorized origins

## API Authentication

All API requests now require JWT token:

```bash
# Get token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}' \
  | jq -r '.token')

# Use token in requests
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/dashboard/stats
```

## Endpoints

### Authentication Endpoints

```
POST   /api/auth/login              - Email/password login
POST   /api/auth/google             - Google OAuth login
GET    /api/auth/me                - Get current user
POST   /api/auth/logout             - Logout
POST   /api/auth/refresh            - Refresh token
```

### Case Endpoints (require auth)

```
GET    /api/cases                   - List cases
GET    /api/cases/{case_id}         - Get case details
GET    /api/judges                  - List judges
GET    /api/dashboard/stats         - Dashboard statistics
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'app'"

**Solution**: Make sure you set `PYTHONPATH` correctly:
```bash
PYTHONPATH=/Volumes/PortableSSD/court-ecosystem/backend python3 -m uvicorn app.main:app
```

### JWT Errors on API Calls

**Solution**: 
1. Ensure token is in `Authorization: Bearer <token>` header
2. Check token hasn't expired (default: 30 days)
3. Check SECRET_KEY matches between login and API (from .env)

### CORS Errors in Browser

**Solution**: Backend already allows all origins in development. If you modify CORS in production:

```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Login Page Not Loading

**Solution**: 
1. Make sure backend is running on port 8000
2. Check browser console for CORS errors
3. Verify `API_BASE_URL` in login.html is correct

## Browser Local Storage

After login, the following are saved:

**localStorage**:
- `token` - JWT token for API auth (30 days expiry)
- `user` - User object with email, name, id

**To logout**: Click "Logout" button or delete localStorage:
```javascript
localStorage.clear()
```

## Development Tips

1. **Clear Cache**: Press `Ctrl+Shift+Delete` to clear browser cache
2. **Check Token**: In DevTools Console:
   ```javascript
   localStorage.getItem('token')
   localStorage.getItem('user')
   ```
3. **Decode Token**: Visit https://jwt.io/ and paste your token
4. **API Testing**: Use Postman or curl with:
   ```
   Authorization: Bearer <token>
   Content-Type: application/json
   ```

## Next Steps

1. [Vercel Deployment Guide](./VERCEL_DEPLOYMENT_GUIDE.md) - Deploy to production
2. [Google OAuth Setup](./VERCEL_DEPLOYMENT_GUIDE.md#step-1-google-oauth-setup) - Add Google login
3. Database Migration - Move to PostgreSQL for production

## Features Implemented

✅ User registration/login (auto-create on first login)
✅ JWT token authentication  
✅ Google OAuth integration
✅ Protected API endpoints
✅ Token refresh mechanism
✅ User profile display
✅ Logout functionality
✅ Persistent login session
✅ Production-ready CORS configuration
✅ Secure password hashing

## Questions or Issues?

Check:
1. Backend logs on terminal
2. Browser DevTools Console tab
3. Network tab for API request/response
4. Local storage for token

---

Ready to deploy? See [VERCEL_DEPLOYMENT_GUIDE.md](./VERCEL_DEPLOYMENT_GUIDE.md)
