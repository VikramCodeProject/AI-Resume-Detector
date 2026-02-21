# Startup Verification Checklist

Run this checklist after using startup.bat or startup.sh to verify everything is working:

## ✅ Pre-Startup Checklist

- [ ] Python 3.10+ installed: `python --version`
- [ ] Node.js installed: `node --version`
- [ ] Git installed: `git --version`
- [ ] In correct directory: `UsMiniProject/`
- [ ] .env file exists: `ls .env` or `dir .env`

## 🚀 Startup Execution

### Windows
```bash
startup.bat
```

### Linux/macOS
```bash
chmod +x startup.sh
./startup.sh
```

## 📋 Post-Startup Verification

### 1. Check Backend is Running
```bash
curl http://localhost:8000/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-02-19T...",
  "environment": "development",
  "version": "1.0.0"
}
```

✅ Backend is ready if you see 200 status code

### 2. Check Frontend is Running
Open in browser: http://localhost:3000

**Expected:**
- White page loads
- Login/Register form visible
- No console errors

✅ Frontend is ready

### 3. Check API Documentation
Open in browser: http://localhost:8000/api/docs

**Expected:**
- Swagger UI loads
- Can see all endpoints listed
- Try-it-out button available

✅ API docs are ready

## 🧪 Integration Tests

Run the comprehensive test suite:

```bash
python test_integration.py
```

**Expected Output:**
```
============================================================
Resume Verification System - Integration Tests
============================================================

✓ Health Check              [PASS]
✓ User Registration         [PASS]
✓ User Login                [PASS]
✓ Resume Listing            [PASS]
✓ Dashboard Stats           [PASS]
✓ GitHub Verification       [PASS]

Total: 6/6 tests passed
✓ All tests passed! System is working correctly.
```

✅ All tests passing = System is fully functional

## 📝 Manual Testing

### 1. Register New User
Go to http://localhost:3000
- Click "Register"
- Enter email, password, name
- Check "I agree to GDPR"
- Click Register

✅ Should see success message

### 2. Login
- Enter email and password
- Click Login

✅ Should be redirected to dashboard

### 3. Upload Resume
- Click "Upload Resume"
- Choose a PDF or DOCX file
- Click Submit

✅ Should show upload progress and complete message

### 4. Check Results
- No errors on page
- Trust score displayed
- Verification details shown

✅ Resume processing complete

## 🔍 Troubleshooting Checks

### Backend Not Responding
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/macOS

# Check backend logs in startup terminal
# Error messages should be visible
```

### Frontend Not Loading
```bash
# Check if port 3000 is in use
netstat -ano | findstr :3000  # Windows
lsof -i :3000                 # Linux/macOS

# Check browser console (F12)
# Look for error messages
```

### Tests Failing
```bash
# Run with verbose output
python test_integration.py

# Check that services are running:
curl http://localhost:8000/api/health
```

### Module Not Found Error
```bash
# Reinstall Python dependencies
python -m pip install -r backend/requirements.txt --force-reinstall

# Reinstall Node dependencies
cd frontend && npm install
```

## 📊 System Requirements Verification

### Disk Space
- Download folder: ~500MB
- node_modules: ~200MB
- venv: ~300MB
- **Total:** ~1GB

### RAM Usage
- Backend: ~50-100MB
- Frontend: ~100-150MB
- **Total:** ~200-300MB

### Network
- No internet required after startup
- APIs called locally only
- GitHub API optional

## 📋 Final Checklist

- [ ] Backend running on localhost:8000
- [ ] Frontend running on localhost:3000
- [ ] API documentation accessible
- [ ] All 6 integration tests pass
- [ ] Can register new user
- [ ] Can login successfully
- [ ] Can upload resume
- [ ] Can view results
- [ ] No error messages in logs

## 🎉 Ready Status

If all checks pass:
- ✅ System is fully functional
- ✅ Ready to develop
- ✅ Ready to test
- ✅ Ready to deploy

## 📞 Support

### If Something's Wrong

1. **Check logs** - Look at terminal output
2. **Run tests** - `python test_integration.py`
3. **Check ports** - Make sure 3000 and 8000 are free
4. **Reinstall** - Remove and reinstall dependencies
5. **Restart** - Close everything and run startup script again

### Still Need Help?

1. Check [QUICKSTART.md](QUICKSTART.md) for common issues
2. Review [README_COMPLETE.md](README_COMPLETE.md) for overview
3. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for solutions

---

**Startup Verification Complete! 🎊**

Your system is ready to use. Visit http://localhost:3000 to begin.

**Status:** ✅ All Systems Go
**Version:** 1.0.0
**Date:** February 19, 2024
