# ✅ Authentication System - Setup Complete!

Your Court Ecosystem application now has a full authentication system with JWT tokens and Google OAuth support. Here's what was added:

## 📁 New Files Created

### Frontend
- **`dashboard/login.html`** - Complete login page with:
  - Email/password login form
  - Google OAuth integration
  - Beautiful, responsive UI
  - Error/success messages
  - Auto-redirect to main dashboard after login

- **`dashboard/index.html`** - Updated with:
  - Auto-redirect to login if not authenticated
  - User email display in navbar
  - Logout button (red button in top-right)
  - JWT token in Authorization header for all API calls

### Backend
- **`backend/app/models/user.py`** - User data model with:
  - Email, password hash, name, Google ID
  - Profile picture support
  - Login tracking
  - is_active flag for account management

- **`backend/app/routes/auth.py`** - Complete auth API endpoints:
  - `POST /api/auth/login` - Email/password login
  - `POST /api/auth/google` - Google OAuth login
  - `GET /api/auth/me` - Get current user info
  - `POST /api/auth/logout` - Logout endpoint
  - `POST /api/auth/refresh` - Refresh JWT token

### Configuration & Documentation
- **`vercel.json`** - Vercel deployment configuration
- **`.env.example`** - Environment variable template
- **`VERCEL_DEPLOYMENT_GUIDE.md`** - Complete Vercel deployment instructions
- **`AUTH_QUICKSTART.md`** - Quick start guide for local development

Updated:
- **`backend/requirements.txt`** - Added PyJWT, google-auth, python-jose
- **`backend/app/main.py`** - Added auth routes and user table initialization

## 🚀 Key Features

✅ **Email/Password Login** - Demo mode: any email/password creates account
✅ **Google OAuth** - 3-click Google sign-in
✅ **JWT Tokens** - Secure, 30-day expiring tokens
✅ **Protected Routes** - All API endpoints require auth
✅ **User Sessions** - localStorage-based persistent login
✅ **Responsive Design** - Mobile-friendly login page
✅ **Error Handling** - User-friendly error messages

## 📦 Installation & Setup

### Step 1: Install New Dependencies

```bash
# Using pip
pip install PyJWT==2.8.1 google-auth==2.25.2 python-jose==3.3.0

# Or update requirements
pip install -r backend/requirements.txt
```

### Step 2: Configure Environment

Edit `backend/.env`:
```bash
SECRET_KEY=your-secret-key-change-this
GOOGLE_CLIENT_ID=your-google-client-id-from-google-console
GOOGLE_CLIENT_SECRET=your-secret-from-google-console
```

### Step 3: Start Backend

```bash
cd backend
PYTHONPATH=/Volumes/PortableSSD/court-ecosystem/backend \
python3 -m uvicorn app.main:app --host localhost --port 8000
```

### Step 4: Access Application

1. Open `dashboard/login.html` in browser
2. Use any email/password to test (auto-creates account)
3. Or use Google OAuth button

## 🔐 Security Notes

- Passwords are hashed with SHA-256
- JWT tokens expire in 30 days
- All API endpoints check JWT token
- CORS configured for local development
- In production: use HTTPS, strong SECRET_KEY, real database

## 🌐 Google OAuth Setup

To enable Google login:

1. Go to https://console.cloud.google.com
2. Create OAuth 2.0 credentials
3. Add authorized origins:
   - `http://localhost:3000`
   - Your Vercel domain (e.g., `https://your-app.vercel.app`)
4. Copy Client ID to `dashboard/login.html`
5. Copy Client ID & Secret to backend `.env`

## 📊 Database Schema

New `users` table created automatically with:
- `id` - UUID primary key
- `email` - Unique user email
- `password_hash` - Hashed password (SHA-256)
- `google_id` - Google OAuth ID
- `name` - User's name
- `profile_picture` - Avatar URL
- `is_active` - Account status
- `created_at` - Registration timestamp
- `last_login` - Last login timestamp

## 🧪 Testing

### Test Email Login (Demo Mode)
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

Response:
```json
{
  "token": "eyJhbGc...",
  "user": {
    "id": "123e...",
    "email": "test@example.com",
    "name": "test"
  }
}
```

### Use Token in API Calls
```bash
curl http://localhost:8000/api/dashboard/stats \
  -H "Authorization: Bearer eyJhbGc..."
```

## 🚢 Deployment to Vercel

See **`VERCEL_DEPLOYMENT_GUIDE.md`** for complete instructions:

1. Deploy backend to Railway/Heroku
2. Push frontend to GitHub
3. Import to Vercel with environment variables
4. Configure Google OAuth URLs
5. Done! 🎉

## ⚙️ API Authentication Flow

```
1. User logs in
   ↓
2. Backend creates JWT token
   ↓
3. Frontend stores token in localStorage
   ↓
4. Frontend adds "Authorization: Bearer <token>" to API requests
   ↓
5. Backend verifies token
   ↓
6. If valid: respond with data
   If invalid/expired: return 401 Unauthorized
```

## 📝 Environment Variables Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `SECRET_KEY` | JWT signing key | `super-secret-key-min-32-chars` |
| `GOOGLE_CLIENT_ID` | Google OAuth ID | `xxxxx.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | Google OAuth Secret | `GOCSPX-xxxxx` |
| `DATABASE_URL` | Database connection | `sqlite:///...` or `postgresql://...` |

## 🔗 Endpoints Summary

### Public Endpoints
- `POST /api/auth/login` - Login with email/password
- `POST /api/auth/google` - Login with Google OAuth

### Protected Endpoints (require JWT token)
- `GET /api/auth/me` - Get current user
- `POST /api/auth/refresh` - Get new token
- `POST /api/auth/logout` - Logout
- `GET /api/cases` - List cases
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/judges` - List judges
- And all other case/dashboard endpoints

## 🐛 Troubleshooting

**"Invalid token" error**
- Check token is passed in Authorization header
- Verify SECRET_KEY matches between login and protected endpoints
- Check token hasn't expired (30 days from creation)

**Google login fails**
- Verify GOOGLE_CLIENT_ID in login.html matches Google Console
- Check authorized origins include your domain
- Clear localStorage and refresh page

**Login redirects to login page**
- Check browser console for errors
- Verify token is saved in localStorage
- Check API response includes token field

**API returns 401**
- User is not authenticated
- Token is invalid or expired
- Authorization header is missing or malformed

## 📚 Quick Links

- [Vercel Deployment Guide](./VERCEL_DEPLOYMENT_GUIDE.md)
- [Quick Start Guide](./AUTH_QUICKSTART.md)
- [.env Template](./.env.example)
- [Google OAuth Docs](https://developers.google.com/identity/gsi/web)

## ✨ What's Next?

1. **Deploy to Vercel** - See VERCEL_DEPLOYMENT_GUIDE.md
2. **Set up PostgreSQL** - For production database
3. **Add password reset** - Email-based password recovery
4. **Email verification** - Confirm email on registration
5. **Two-factor auth** - Additional security layer
6. **Role-based access** - Admin, lawyer, user roles

## 📞 Support

For issues, check:
1. Backend logs in terminal
2. Browser console (F12)
3. Network tab for API requests
4. `localStorage` for token presence

---

**🎉 Authentication system is ready to use!**

Start the backend and open `dashboard/login.html` to test it out!
