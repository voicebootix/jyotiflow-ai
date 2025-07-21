@echo off
echo.
echo 🚀 Creating Pull Request for Social Media Save Fixes
echo =====================================================
echo.

REM Get current branch
for /f "delims=" %%i in ('git branch --show-current') do set CURRENT_BRANCH=%%i
echo Current Branch: %CURRENT_BRANCH%

REM Get repository remote URL
for /f "delims=" %%i in ('git remote get-url origin') do set REPO_URL=%%i
echo Repository: %REPO_URL%

REM Extract GitHub repository path
set REPO_URL=%REPO_URL:https://github.com/=%
set REPO_URL=%REPO_URL:.git=%
echo Repository Path: %REPO_URL%

echo.
echo 📋 Pull Request Details:
echo ------------------------
echo Title: 🚨 Critical Fix: Social Media Configuration Save Failures in Admin Dashboard
echo Branch: %CURRENT_BRANCH%
echo Base: main
echo.

REM Create PR URL
set PR_URL=https://github.com/%REPO_URL%/compare/main...%CURRENT_BRANCH%

echo 🔗 Pull Request Creation URL:
echo %PR_URL%
echo.

echo 📝 Opening GitHub in browser...
start "" "%PR_URL%"

echo.
echo ✅ Instructions:
echo 1. Browser should open to GitHub PR creation page
echo 2. Copy title from above if not auto-filled
echo 3. Copy description from PULL_REQUEST_DESCRIPTION.md
echo 4. Add labels: bug, critical, admin-dashboard, authentication
echo 5. Click "Create pull request"
echo.

pause 