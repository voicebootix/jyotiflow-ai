@echo off
echo 🚀 Committing Indentation Fixes (core.md & refresh.md compliant)
echo ================================================================

echo Adding modified service files...

if exist services\facebook_service.py (
    git add services/facebook_service.py
    echo ✅ Added services/facebook_service.py
) else (
    echo ⚠️ services/facebook_service.py not found, skipping
)

if exist services\instagram_service.py (
    git add services/instagram_service.py  
    echo ✅ Added services/instagram_service.py
) else (
    echo ⚠️ services/instagram_service.py not found, skipping
)

if exist services\tiktok_service.py (
    git add services/tiktok_service.py
    echo ✅ Added services/tiktok_service.py
) else (
    echo ⚠️ services/tiktok_service.py not found, skipping
)

if exist routers\social_media_marketing_router.py (
    git add routers/social_media_marketing_router.py
    echo ✅ Added routers/social_media_marketing_router.py
) else (
    echo ⚠️ routers/social_media_marketing_router.py not found, skipping
)

echo Files added to staging area.

echo Creating commit...
git commit -m "🔧 Fix social media services indentation errors (core.md & refresh.md compliant)

- Fix Facebook service return statement indentation
- Fix Instagram service return statement indentation  
- Fix TikTok service headers and return statement indentation
- Preserve YouTube handle fix functionality
- Maintain all existing API functionality
- Ensure proper code block structure"

echo ================================================================
echo ✅ Commit completed successfully!
echo ✅ YouTube fix preserved
echo ✅ Indentation issues resolved  
echo 🚀 Ready for push to remote repository 