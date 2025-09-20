# 🚀 Heroku Deployment Guide
## Occupational Health Assistant

This guide will help you deploy the Occupational Health Assistant to Heroku for production use.

## 📋 Prerequisites

1. **Heroku Account**: Create a free account at [heroku.com](https://heroku.com)
2. **Heroku CLI**: Install from [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)
3. **Git**: Ensure git is installed
4. **Google Cloud Credentials**: You'll need service account credentials
5. **Email Credentials**: Gmail app password for sending emails

## 🎯 Quick Deploy (One-Click)

If you just want to get the app running quickly:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

This will use the `app.json` configuration to automatically deploy with required environment variables.

## 📁 File Structure Overview

The deployment package contains everything needed for Heroku:

```
deployment_package/
├── app.py                    # Main FastAPI application
├── Procfile                  # Heroku process definition
├── runtime.txt               # Python version specification
├── requirements.txt          # Python dependencies
├── app.json                  # Heroku app configuration
├── MY_CREDENTIALS.txt        # Your actual credentials
├── src/                      # Source code
├── html_version/             # Frontend files
├── multi_agent_prompt/       # AI prompts
└── patient_prompt/           # Patient scenarios
```

## 🔧 Manual Deployment Steps

### Step 1: Prepare Your Environment

```bash
# Clone or navigate to the deployment package
cd deployment_package

# Login to Heroku
heroku login

# Create a new Heroku app
heroku create your-app-name-here
```

### Step 2: Configure Environment Variables

Set all required environment variables on Heroku:

```bash
# Google Cloud Configuration
heroku config:set GOOGLE_CLOUD_PROJECT="ferrous-quest-472519-f1"
heroku config:set GEMINI_API_KEY="AIzaSyA33KWSyyVK_gMsuxXSkLvpceNIv6HHuVI"

# Email Configuration (Updated)
heroku config:set SMTP_USERNAME="team@monashmed.tech"
heroku config:set EMAIL_PASSWORD="dorf fmxi xchk hgpu"
```

### Step 3: Setup Google Cloud Authentication

For Vertex AI to work on Heroku, you need to set up service account authentication:

```bash
# Create a service account key file (JSON)
# Go to Google Cloud Console > IAM & Admin > Service Accounts
# Create a new service account with Vertex AI User role
# Download the JSON key file

# Convert the JSON file to a base64 string
base64 -i path/to/your-service-account-key.json

# Set the credentials as an environment variable
heroku config:set GOOGLE_APPLICATION_CREDENTIALS_JSON="your-base64-encoded-json-here"
```

### Step 4: Update Code for Heroku Authentication

The deployment package is already configured to handle this. The `src/ai/llm_client.py` file will automatically use the JSON credentials from the environment variable.

### Step 5: Deploy to Heroku

```bash
# Initialize git repository (if not already done)
git init
git add .
git commit -m "Initial deployment to Heroku"

# Set Heroku as remote and deploy
heroku git:remote -a your-app-name-here
git push heroku main
```

### Step 6: Scale and Monitor

```bash
# Ensure at least one web dyno is running
heroku ps:scale web=1

# View logs
heroku logs --tail

# Open your app
heroku open
```

## 🌐 Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `GOOGLE_CLOUD_PROJECT` | Your Google Cloud Project ID | `ferrous-quest-472519-f1` |
| `GEMINI_API_KEY` | Google Gemini API key for chat | `AIzaSy...` |
| `SMTP_USERNAME` | Email address for sending reports | `team@monashmed.tech` |
| `EMAIL_PASSWORD` | Gmail app password | `dorf fmxi xchk hgpu` |
| `GOOGLE_APPLICATION_CREDENTIALS_JSON` | Base64 encoded service account JSON | `eyJ0eXBlI...` |

## 🔍 Verification Steps

After deployment, verify everything works:

1. **Visit your app URL**: `https://your-app-name.herokuapp.com`
2. **Test chat functionality**: Start a conversation with Dr. O
3. **Test summary generation**: Complete an interview and generate a summary
4. **Test email sending**: Send a summary to verify email functionality

## 🐛 Troubleshooting

### Common Issues:

**1. Application Error on Startup**
```bash
# Check logs
heroku logs --tail

# Common causes:
# - Missing environment variables
# - Python version mismatch
# - Dependency issues
```

**2. Email Not Sending**
```bash
# Verify email credentials
heroku config:get SMTP_USERNAME
heroku config:get EMAIL_PASSWORD

# Test email configuration
heroku run python -c "
import os
print('SMTP Username:', os.getenv('SMTP_USERNAME'))
print('Email Password Set:', bool(os.getenv('EMAIL_PASSWORD')))
"
```

**3. Vertex AI Authentication Errors**
```bash
# Verify Google Cloud credentials
heroku config:get GOOGLE_CLOUD_PROJECT
heroku config:get GOOGLE_APPLICATION_CREDENTIALS_JSON

# Test Vertex AI connection
heroku run python -c "
import os, base64, json, tempfile
import vertexai

# Decode credentials
creds_json = base64.b64decode(os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON'))
creds_dict = json.loads(creds_json)

# Create temporary file
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(creds_dict, f)
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f.name

# Test Vertex AI
project = os.getenv('GOOGLE_CLOUD_PROJECT')
vertexai.init(project=project, location='us-central1')
print('✅ Vertex AI connection successful')
"
```

**4. Static Files Not Loading**
- Ensure `html_version/` directory is included in your git commit
- Check Heroku logs for 404 errors on static files

## 📊 Monitoring and Maintenance

### View Application Metrics:
```bash
# View dyno usage
heroku ps

# View application metrics
heroku logs --tail

# View config variables
heroku config
```

### Updating the Application:
```bash
# Make changes to your code
git add .
git commit -m "Update application"
git push heroku main

# Restart dynos if needed
heroku restart
```

## 💰 Cost Considerations

- **Heroku Eco Dyno**: Free tier, sleeps after 30 minutes of inactivity
- **Basic Dyno**: $7/month, never sleeps
- **Standard Dynos**: $25+/month for production workloads

For production use, consider:
- Using at least Basic dyno to prevent sleeping
- Adding Heroku Postgres for session persistence
- Setting up monitoring and alerting

## 🔐 Security Best Practices

1. **Environment Variables**: Never hardcode credentials in your code
2. **HTTPS**: Heroku apps automatically use HTTPS
3. **Secrets Rotation**: Regularly rotate API keys and passwords
4. **Access Control**: Limit who has access to your Heroku app
5. **Logging**: Monitor logs for suspicious activity

## 📚 Additional Resources

- [Heroku Python Documentation](https://devcenter.heroku.com/articles/getting-started-with-python)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/heroku/)
- [Google Cloud Authentication](https://cloud.google.com/docs/authentication/getting-started)

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review Heroku logs: `heroku logs --tail`
3. Verify all environment variables are set correctly
4. Ensure your Google Cloud project has the necessary APIs enabled

---

**🎉 Congratulations!** Your Occupational Health Assistant should now be running on Heroku and accessible to users worldwide.
