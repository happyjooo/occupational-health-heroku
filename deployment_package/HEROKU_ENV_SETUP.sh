#!/bin/bash
# 🚀 Heroku Environment Variables Setup Script
# Run this script to set all environment variables for your Heroku app

echo "🔧 Setting up Heroku environment variables..."
echo "📧 Note: This uses the updated team@monashmed.tech email"

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not found. Please install it first:"
    echo "   https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Get app name from user
read -p "Enter your Heroku app name: " APP_NAME

echo "🏗️  Setting environment variables for app: $APP_NAME"

# Set all environment variables
heroku config:set GOOGLE_CLOUD_PROJECT="ferrous-quest-472519-f1" -a $APP_NAME
heroku config:set GEMINI_API_KEY="AIzaSyA33KWSyyVK_gMsuxXSkLvpceNIv6HHuVI" -a $APP_NAME
heroku config:set SMTP_USERNAME="team@monashmed.tech" -a $APP_NAME
heroku config:set EMAIL_PASSWORD="dorf fmxi xchk hgpu" -a $APP_NAME

echo "✅ Environment variables set successfully!"
echo ""
echo "📋 Verification - Current config:"
heroku config -a $APP_NAME

echo ""
echo "🚀 Next steps:"
echo "1. Ensure your service account JSON is set up for Google Cloud"
echo "2. Deploy your code: git push heroku main"
echo "3. Scale web dyno: heroku ps:scale web=1 -a $APP_NAME"
echo "4. Open your app: heroku open -a $APP_NAME"
