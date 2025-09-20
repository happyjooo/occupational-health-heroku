# 🔐 Security & Credentials Setup Guide

## ⚠️ **IMPORTANT**: No Shared Credentials

**Your friend will need to set up her OWN credentials. None of your personal credentials are included in this deployment package.**

## 🚨 **What's NOT Included (Security)**

✅ **Safe**: No personal credentials in the code
- ❌ No Google Cloud project IDs
- ❌ No Gmail passwords  
- ❌ No service account keys
- ❌ No API keys

## 🛡️ **What Your Friend Must Set Up**

### 1. 🎯 **Google Cloud Project (Required)**

Your friend needs her **OWN** Google Cloud project:

```bash
# 1. Create new project at: https://console.cloud.google.com
# 2. Enable these APIs:
#    - Vertex AI API
#    - Generative AI API  
# 3. Set up billing (required for Vertex AI)
# 4. Note the project ID
```

**💰 Cost**: ~$0.01-0.10 per conversation (very affordable)

### 2. 📧 **Email Setup (Required)**

Your friend needs her **OWN** Gmail account:

```bash
# 1. Use any Gmail account she controls
# 2. Enable 2-factor authentication
# 3. Generate App Password:
#    - Go to Google Account → Security → App passwords
#    - Create password for "Mail"
#    - Save the 16-character password
```

### 3. 🔑 **Environment Variables**

For **Local Development**:
```bash
export GOOGLE_CLOUD_PROJECT="her-project-id"
export SMTP_USERNAME="her-email@gmail.com"  
export EMAIL_PASSWORD="her-gmail-app-password"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/her-service-account.json"
```

For **Production Deployment** (Heroku, Railway, Vercel, etc.):
- Set these as **secret environment variables** in the platform dashboard
- **Never** put credentials in code or commit them to git

## 🚀 **Deployment Platform Examples**

### Heroku
```bash
heroku config:set GOOGLE_CLOUD_PROJECT="her-project-id"
heroku config:set SMTP_USERNAME="her-email@gmail.com"
heroku config:set EMAIL_PASSWORD="her-gmail-app-password"
# Upload service account JSON through Heroku dashboard
```

### Railway
- Go to project settings → Environment Variables
- Add each variable as a secret
- Upload service account JSON as a file

### Vercel
- Go to project settings → Environment Variables  
- Add variables with "Production" environment selected
- Upload service account JSON through dashboard

## 🔒 **Security Best Practices**

1. **Never share credentials** between projects
2. **Use service accounts** for production (not personal Google accounts)
3. **Rotate credentials** regularly
4. **Use platform-specific secret managers** for production
5. **Set up monitoring** for unusual API usage

## 🆘 **Troubleshooting**

### Google Cloud Issues
```bash
# Test authentication
gcloud auth application-default login
gcloud auth list

# Test project access
gcloud config set project her-project-id
gcloud services list --enabled
```

### Email Issues
```bash
# Test Gmail credentials
# Create a simple Python script to test SMTP connection
python -c "
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('her-email@gmail.com', 'her-app-password')
print('✅ Email credentials work!')
server.quit()
"
```

## 💡 **Cost Optimization**

- **Vertex AI**: Use `us-central1` region (cheapest)
- **Gemini API**: Has generous free tier  
- **Email**: Gmail is free
- **Hosting**: Many platforms have free tiers

## 📞 **Support**

If your friend encounters issues:
1. Check environment variables are set correctly
2. Verify Google Cloud APIs are enabled
3. Test Gmail app password separately
4. Check billing is set up for Google Cloud










