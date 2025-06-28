# Django Backend Integration Guide

This guide explains how to connect the React frontend to your Django backend.

## 🔗 Current Integration Status

✅ **Frontend Ready**: React app is configured to call Django endpoints
✅ **API Service**: Configured to match your Django URL structure
✅ **Authentication**: Login/logout endpoints mapped
✅ **Error Handling**: Proper error handling for API calls

## 🚀 Quick Setup

### 1. Start Django Backend
```bash
cd Backend
python manage.py runserver
```

### 2. Start React Frontend
```bash
cd Tirum
npm run dev
```

### 3. Test the Integration
- Frontend: http://localhost:5173
- Backend: http://localhost:8000

## 📡 API Endpoints Mapping

### Authentication Endpoints
| Frontend | Django Backend | Method | Purpose |
|----------|----------------|--------|---------|
| `/api/login/` | `/api/login/` | POST | User login |
| `/api/logout/` | `/api/logout/` | POST | User logout |
| `/api/user/` | `/api/user/` | GET | Get current user |

### Your Django Endpoints
The frontend is also configured for your other endpoints:
- `/api/expense-categories/`
- `/api/transactions/`
- `/api/split-details/`
- `/api/khata-entries/`
- `/api/notifications/`
- `/api/bill-reminders/`
- `/api/wallets/`
- `/api/user-summary/`

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the `Tirum` directory:
```env
VITE_API_URL=http://localhost:8000/api
```

### CORS Configuration
Make sure your Django backend allows CORS from the React frontend:

```python
# In your Django settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # React dev server
    "http://127.0.0.1:5173",
]

CORS_ALLOW_CREDENTIALS = True
```

## 🧪 Testing the Integration

### 1. Test Login
1. Go to http://localhost:5173
2. You'll be redirected to the login page
3. Use your Django user credentials
4. Check browser console for API calls

### 2. Check Network Tab
Open browser DevTools → Network tab to see:
- API requests to Django backend
- Response status codes
- Response data format

### 3. Test Error Handling
Try invalid credentials to see error handling in action.

## 🔍 Debugging

### Common Issues

1. **CORS Errors**
   - Check Django CORS settings
   - Ensure frontend URL is allowed

2. **404 Errors**
   - Verify Django server is running
   - Check URL patterns in Django urls.py

3. **Authentication Errors**
   - Check Django authentication backend
   - Verify token format in response

### Debug Steps

1. **Check Django Logs**
   ```bash
   python manage.py runserver --verbosity=2
   ```

2. **Check Browser Console**
   - Network tab for API calls
   - Console tab for JavaScript errors

3. **Test API Directly**
   ```bash
   curl -X POST http://localhost:8000/api/login/ \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"password"}'
   ```

## 📝 Response Format

The frontend expects this response format from Django:

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "User Name",
    "avatar": "https://example.com/avatar.jpg"
  },
  "token": "your-jwt-token-here"
}
```

## 🔄 Next Steps

1. **Test with Real Users**: Create users in Django admin
2. **Add Registration**: Implement signup functionality
3. **Add Password Reset**: Implement password recovery
4. **Add Profile Management**: User profile editing
5. **Add Your Features**: Integrate expense tracking, khata, etc.

## 🎯 Success Indicators

✅ Login form submits to Django backend
✅ Successful login redirects to dashboard
✅ User data displays correctly
✅ Logout clears session
✅ Protected routes work properly

Your React frontend is now fully integrated with your Django backend! 🎉 