# 🏥 Occupational Health Assistant - Deployment Ready

This package contains everything needed to deploy the Occupational Health Assistant to **Heroku**.

## 📧 Current Configuration

- **Email**: `team@monashmed.tech`
- **App Password**: `dorf fmxi xchk hgpu`
- **Google Cloud Project**: `ferrous-quest-472519-f1`
- **Gemini API Key**: `AIzaSyA33KWSyyVK_gMsuxXSkLvpceNIv6HHuVI`

## 🚀 Quick Heroku Deployment

### Option 1: One-Click Deploy
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

### Option 2: Manual Deploy
```bash
# 1. Login to Heroku
heroku login

# 2. Create app
heroku create your-app-name

# 3. Set environment variables (use the script)
./HEROKU_ENV_SETUP.sh

# 4. Deploy
git init
git add .
git commit -m "Deploy to Heroku"
heroku git:remote -a your-app-name
git push heroku main

# 5. Scale
heroku ps:scale web=1

# 6. Open
heroku open
```

## 📁 Key Files

- `app.py` - Main FastAPI application
- `Procfile` - Heroku process definition
- `requirements.txt` - Python dependencies
- `HEROKU_DEPLOYMENT_GUIDE.md` - Detailed deployment instructions
- `HEROKU_ENV_SETUP.sh` - Script to set environment variables

## 🔧 Environment Variables Set

The deployment automatically configures:
- ✅ `GOOGLE_CLOUD_PROJECT`
- ✅ `GEMINI_API_KEY` 
- ✅ `SMTP_USERNAME`
- ✅ `EMAIL_PASSWORD`

## 🌐 What the App Does

1. **Chat Interface**: Patients interact with Dr. O (AI assistant)
2. **Summary Generation**: Creates patient-facing summaries
3. **Doctor Reports**: Generates detailed PDF reports for doctors
4. **Email Delivery**: Sends reports to selected doctors

## 📊 Post-Deployment Testing

1. Visit your Heroku app URL
2. Start a chat session
3. Complete an occupational history interview
4. Generate and review summary
5. Send report to doctor (test email functionality)

## 🆘 Troubleshooting

Check logs: `heroku logs --tail`

Common issues:
- **Email not sending**: Verify `SMTP_USERNAME` and `EMAIL_PASSWORD`
- **AI not working**: Check `GEMINI_API_KEY` and `GOOGLE_CLOUD_PROJECT`
- **App crash**: Check Python dependencies in `requirements.txt`

---

**Ready to deploy!** 🎉
