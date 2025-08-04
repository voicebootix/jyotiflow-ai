# 🛡️ Haar Cascade Assets Deployment Guide

## 📁 Required Files for Face Detection

The `backend/assets/` directory contains critical files for OpenCV face detection:

```
backend/assets/
├── haarcascade_frontalface_default.xml  # Required for face detection
├── swamiji_base_image.png               # Base avatar image
└── DEPLOYMENT_GUIDE.md                  # This guide
```

## 🚀 Deployment Environment Setup

### **Option 1: Environment Variable (Recommended)**
Set the cascade file path via environment variable:

```bash
# For Render/Docker/Cloud deployments
HAAR_CASCADE_PATH=/app/assets/haarcascade_frontalface_default.xml

# For local development  
HAAR_CASCADE_PATH=backend/assets/haarcascade_frontalface_default.xml
```

### **Option 2: Automatic Path Detection**
The system automatically tries these paths in order:
1. `backend/assets/haarcascade_frontalface_default.xml` (local dev)
2. `assets/haarcascade_frontalface_default.xml` (deployed)
3. `/app/backend/assets/haarcascade_frontalface_default.xml` (Docker)
4. Relative to service file location

## 📦 Platform-Specific Instructions

### **Render Deployment**
Ensure `backend/assets/` is included in your build:

```yaml
# render.yaml (if using)
services:
  - type: web
    name: jyotiflow-api
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python main.py"
    envVars:
      - key: HAAR_CASCADE_PATH
        value: /opt/render/project/src/backend/assets/haarcascade_frontalface_default.xml
```

### **Docker Deployment**
Include assets in your Dockerfile:

```dockerfile
COPY backend/assets/ /app/backend/assets/
ENV HAAR_CASCADE_PATH=/app/backend/assets/haarcascade_frontalface_default.xml
```

### **Local Development**
Assets should work automatically with relative paths.

## ⚠️ Troubleshooting

### **Error: "Haar Cascade file not found"**
1. Check if `backend/assets/haarcascade_frontalface_default.xml` exists
2. Set `HAAR_CASCADE_PATH` environment variable
3. Verify file permissions (readable)
4. Check deployment logs for path attempts

### **Error: "Failed to load Haar Cascade"**
1. File exists but is corrupted - re-download from OpenCV
2. Check file size (should be ~900KB)
3. Verify it's the correct XML format

### **Fallback Behavior**
If cascade loading fails, the system automatically falls back to:
- Simple center-based face detection
- Larger protection zone for safety
- Logs warning message for debugging

## 🔧 Testing Face Detection

```python
# Test cascade loading in Python
import cv2
import os

cascade_path = "backend/assets/haarcascade_frontalface_default.xml"
if os.path.isfile(cascade_path):
    cascade = cv2.CascadeClassifier(cascade_path)
    if not cascade.empty():
        print("✅ Cascade loaded successfully")
    else:
        print("❌ Cascade file corrupted")
else:
    print("❌ Cascade file not found")
```

## 📋 Deployment Checklist

- [ ] `backend/assets/` directory included in deployment
- [ ] `haarcascade_frontalface_default.xml` file present  
- [ ] File permissions are readable
- [ ] Environment variable set (if using custom path)
- [ ] Test face detection endpoint after deployment
- [ ] Check logs for cascade loading success/failure

## 🎯 Expected Behavior

**✅ Success:** 
- "Successfully loaded Haar Cascade from: [path]"
- Advanced OpenCV face detection enabled
- Precise face location and protection

**⚠️ Fallback:**
- "Haar Cascade loading failed: [error]"  
- "Falling back to simple center-based face detection"
- Still functional, but less precise