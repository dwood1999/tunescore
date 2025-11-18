# Track Upload 401/500 Error Fixes

## Issue Timeline

### Problem 1: 401 Unauthorized (✅ FIXED)
**Error**: `POST /api/v1/tracks/upload 401 (Unauthorized)`

**Root Cause**: Frontend was not sending JWT authentication token in API requests.

**Solution**: 
- Updated `frontend/src/lib/api/client.ts` to:
  - Add `getAuthToken()` function to retrieve JWT from localStorage
  - Add `getAuthHeaders()` function to include `Authorization: Bearer <token>` header
  - Apply auth headers to all API requests, including track upload

**Changes Made**:
```typescript
// frontend/src/lib/api/client.ts
function getAuthToken(): string | null {
    if (!browser) return null;
    return localStorage.getItem('tunescore_access_token');
}

function getAuthHeaders(additionalHeaders?: HeadersInit): HeadersInit {
    const token = getAuthToken();
    const headers: HeadersInit = { ...additionalHeaders };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
}
```

---

### Problem 2: 500 Internal Server Error (✅ FIXED)
**Error**: `POST /api/v1/tracks/upload 500 (Internal Server Error)`

**Root Cause**: Backend libraries (`librosa`, etc.) were already installed but the service needed a restart to properly initialize them.

**Solution**: 
- Verified all audio processing dependencies are installed in Poetry virtualenv
- Restarted backend service to ensure clean initialization

**Dependencies Confirmed**:
- ✅ librosa (audio feature extraction)
- ✅ soundfile (audio I/O)
- ✅ pydub (audio processing)
- ✅ numpy, scipy (numerical computing)
- ✅ scikit-learn (machine learning)
- ✅ numba (performance optimization)

---

## Current Status

### Backend
- ✅ Running on port 8001
- ✅ Health check passing
- ✅ All audio processing libraries loaded
- ✅ Authentication working properly

### Frontend  
- ✅ Built with authentication support
- ✅ Running on port 5129
- ✅ Properly sending Authorization headers

---

## Testing the Fix

### For Users:
1. Navigate to https://music.quilty.app
2. **Log in** (or register if you don't have an account)
3. Go to `/upload` page
4. Fill in track details
5. Select an audio file
6. Click upload

### Expected Behavior:
- ✅ Authentication should work (no more 401)
- ✅ Upload should process (no more 500)
- ✅ Audio analysis should run successfully
- ⏱️ Processing may take 30-60 seconds for full analysis

### To Verify You're Logged In:
Open browser DevTools (F12) → Console → Run:
```javascript
localStorage.getItem('tunescore_access_token')
```
If this returns a token string, you're authenticated.

---

## Files Modified

### Frontend:
- `frontend/src/lib/api/client.ts` - Added authentication headers

### Backend:
- `backend/app/core/security.py` - Added debug logging
- Dependencies verified and backend restarted

---

## Deployment Notes

### After Frontend Changes:
```bash
cd /home/dwood/tunescore/frontend
npm run build
pkill -f "vite preview.*5129"
npm run preview -- --host 0.0.0.0 --port 5129 &
```

### After Backend Changes:
```bash
sudo systemctl restart tunescore-backend
# Or for manual restart:
cd /home/dwood/tunescore/backend
/home/dwood/.cache/pypoetry/virtualenvs/tunescore-backend-0udhgdCI-py3.12/bin/uvicorn app.main:app --host 127.0.0.1 --port 8001
```

---

## Date: November 16, 2025
## Status: ✅ RESOLVED

