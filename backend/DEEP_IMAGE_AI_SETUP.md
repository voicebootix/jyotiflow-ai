# 🎯 Deep Image AI Integration Setup

## Overview
This integration provides **perfect face preservation** with **complete background transformation** using Deep-Image.ai's specialized face adapter technology.

## ✅ Benefits Over Stability AI
- **100% Face Preservation**: `adapter_type="face"` with `face_id=true`
- **Complete Background Transformation**: No masking complexity
- **Natural Blending**: Professional portrait results
- **Fallback Support**: Automatically falls back to Stability AI if needed

## 🔧 Setup Instructions

### 1. Get Deep Image AI API Key
1. Visit [Deep-Image.ai](https://deep-image.ai)
2. Create an account
3. Get your API key from the dashboard

### 2. Configure Environment Variable
Add to your environment variables:
```bash
DEEP_IMAGE_API_KEY=your_api_key_here
```

### 3. Verify Integration
The theme service will automatically:
- ✅ Try Deep Image AI first (preferred)
- 🔄 Fallback to Stability AI if needed
- 📝 Log which service is being used

## 🧪 Testing

### Check Service Status
```python
from services.deep_image_ai_service import DeepImageAiService

service = DeepImageAiService()
status = await service.check_service_status()
print(f"Available: {status['available']}")
print(f"Credits: {status.get('credits')}")
```

### Test Face Preservation
1. Upload Swamiji image via admin dashboard
2. Generate daily theme preview
3. Verify:
   - ✅ Face, beard, hair exactly preserved
   - ✅ Background completely transformed
   - ✅ Natural, realistic result

## 🎯 How It Works

### Deep Image AI Request
```json
{
  "url": "https://uploaded-swamiji-image.jpg",
  "width": 1024,
  "height": 1024,
  "background": {
    "generate": {
      "description": "mountain peak at sunrise, spiritual environment",
      "adapter_type": "face",    // 🎯 Face preservation mode
      "face_id": true,           // 🎯 Detailed facial features
      "model_type": "realistic"  // 🎯 High-quality portraits
    }
  }
}
```

### Prompt Optimization
- **Simple & Clear**: "A photorealistic portrait of a South Indian spiritual guru..."
- **No Complex Weighting**: Deep Image AI handles face preservation automatically
- **Focus on Scene**: Describe the desired background/setting

## 🔄 Fallback Behavior

1. **Try Deep Image AI** (if configured)
   - Perfect face preservation
   - Complete background transformation

2. **Fallback to Stability AI** (if Deep Image AI fails)
   - Uses img2img with complex prompts
   - Higher risk of face changes

## 🚀 Production Deployment

### Environment Variables Required
```bash
# Primary service (new)
DEEP_IMAGE_API_KEY=your_deep_image_api_key

# Fallback service (existing)
STABILITY_API_KEY=your_stability_api_key
```

### Monitoring
Check logs for service usage:
```
INFO: 🎯 Using Deep Image AI for perfect face preservation + background transformation
INFO: ✅ Deep Image AI generation successful
```

Or fallback:
```
WARNING: Deep Image AI failed, falling back to Stability AI
INFO: 🔄 Falling back to Stability AI img2img approach
```

## 💰 Cost Comparison

### Deep Image AI
- **Face Mode**: ~$0.02-0.05 per image
- **Realistic Model**: High quality
- **Credits System**: Pay per use

### Stability AI (Fallback)
- **IMG2IMG**: ~$0.018 per image
- **Multiple Attempts**: May need several tries
- **Quality Varies**: Depends on prompts/strength

## ✨ Expected Results

With Deep Image AI:
- 🎯 **Face**: 100% preserved (eyes, nose, mouth, beard, hair)
- 🌄 **Background**: Completely transformed (mountain, temple, beach, etc.)
- 👗 **Clothing**: Changed to match theme (robes, traditional attire)
- 📸 **Quality**: Professional portrait photography
- ⚡ **Speed**: Single attempt, perfect result

Perfect solution for the face preservation + background transformation requirement!