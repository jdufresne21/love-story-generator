#!/bin/bash

echo "🚂 Railway Deployment Helper"
echo "============================"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git repository not found. Initializing..."
    git init
    git add .
    git commit -m "Initial commit for Railway deployment"
    echo "✅ Git repository initialized"
    echo ""
    echo "⚠️  IMPORTANT: You need to create a GitHub repository and push your code:"
    echo "1. Go to GitHub.com and create a new repository"
    echo "2. Run these commands (replace with your actual repo URL):"
    echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git"
    echo "   git branch -M main"
    echo "   git push -u origin main"
    echo ""
else
    echo "✅ Git repository found"
    
    # Check if there are uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        echo "📝 Uncommitted changes found. Committing..."
        git add .
        git commit -m "Update for Railway deployment"
        echo "✅ Changes committed"
    else
        echo "✅ No uncommitted changes"
    fi
fi

echo ""
echo "📋 Deployment Checklist:"
echo "1. ✅ Code is ready for deployment"
echo "2. ✅ Procfile created"
echo "3. ✅ requirements.txt updated"
echo "4. ✅ runtime.txt specified"
echo "5. ✅ .gitignore configured"
echo ""
echo "🚀 Next Steps:"
echo "1. Push your code to GitHub (if not done already)"
echo "2. Go to railway.app and create a new project"
echo "3. Connect your GitHub repository"
echo "4. Add your OPENAI_API_KEY as an environment variable"
echo "5. Deploy!"
echo ""
echo "📖 See DEPLOYMENT.md for detailed instructions" 