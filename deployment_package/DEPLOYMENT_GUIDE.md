# 🚀 Occupational History AI - Deployment Guide

## 🚀 **OPTION 1: Quick Start with Provided Credentials** (Recommended First)

### **📋 Prerequisites**
- Python 3.9 or higher
- That's it! (Credentials provided in `CREDENTIALS_TEMPLATE.txt`)

### **⚡ Super Quick Setup (5 minutes)**

**1. Install Dependencies**
```bash
pip install -r requirements.txt
```

**2. Get Your Credentials**
- Look for `MY_CREDENTIALS.txt` with CJ's actual credentials filled in
- **Copy the export commands** directly from that file

**3. Set Environment Variables**
```bash
# Copy these EXACT commands from MY_CREDENTIALS.txt:
export GOOGLE_CLOUD_PROJECT="cj-actual-project-id"
export SMTP_USERNAME="cj-actual-email@gmail.com"
export EMAIL_PASSWORD="cj-actual-16-char-password"
```

**4. Start the Application**
```bash
python app.py
```

**5. Test It's Working**
- Visit: `http://localhost:8000`
- Visit: `http://localhost:8000/debug` to test all features

✅ **That's it! The app should work immediately with my credentials.**

---

## 🏥 **OPTION 2: Lab Deployment with Your Own Credentials** (Later)

### **When the lab wants to use their own Google Cloud account:**

**1. Create Lab Google Cloud Project**
```bash
# 1. Go to: https://console.cloud.google.com
# 2. Create new project for the lab
# 3. Enable these APIs:
#    - Vertex AI API
#    - Generative AI API
# 4. Note the new project ID
```

**2. Set Up Lab Gmail**
```bash
# 1. Use lab Gmail account
# 2. Go to: https://myaccount.google.com
# 3. Security → 2-Step Verification (enable)
# 4. Security → App passwords → Generate for "Mail"
# 5. Note the 16-character password
```

**3. Update Credentials**
- Edit `MY_CREDENTIALS.txt` with lab values
- Run the new export commands  
- Restart the server
- **📖 See `CREDENTIAL_SWITCHING_GUIDE.md` for detailed step-by-step instructions**

**4. Authenticate with Lab Google Cloud**
```bash
# Option A: Service Account (Production)
# 1. Create service account in Google Cloud Console
# 2. Download JSON key file
# 3. Set path:
export GOOGLE_APPLICATION_CREDENTIALS="path/to/lab-service-account-key.json"

# Option B: User Authentication (Development)
gcloud auth application-default login
```

---

## 🔄 **Easy Credential Switching**

**To switch from my credentials to lab credentials:**

1. **Update** `CREDENTIALS_TEMPLATE.txt` with new values
2. **Copy** the export commands
3. **Run** them in terminal
4. **Restart** the application
5. **Test** at `/debug` interface

**Verification Commands:**
```bash
echo "Project: $GOOGLE_CLOUD_PROJECT"
echo "Email: $SMTP_USERNAME" 
echo "Password Set: $(if [ -n "$EMAIL_PASSWORD" ]; then echo 'YES'; else echo 'NO'; fi)"
```

## 📁 File Structure

```
deployment_package/
├── app.py                    # Main FastAPI application
├── manual_table_converter.py # PDF generation utility
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── DEPLOYMENT_GUIDE.md       # This file
├── src/                      # Core application logic
│   ├── ai/                   # AI conversation management
│   ├── api/                  # API utilities (unused in current version)
│   ├── evaluation/           # Patient simulation (unused in current version)
│   ├── prompts/             # Legacy prompts
│   └── reports/             # PDF generation
├── html_version/            # Frontend web interface
│   ├── index.html           # Landing page
│   ├── chat.html            # Chat interface
│   ├── review.html          # Summary review page
│   ├── success.html         # Success confirmation
│   └── debug.html           # Debug interface (optional)
├── multi_agent_prompt/      # AI system prompts
└── patient_prompt/          # Patient persona prompts
```

## 🔧 Configuration

### Email Configuration
The application automatically uses your environment variables:
```python
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "your-email@gmail.com")
SMTP_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
```

**⚠️ Important**: Set both `SMTP_USERNAME` and `EMAIL_PASSWORD` environment variables for email to work.

### Google Cloud Configuration
The application uses:
- **Gemini 2.5 Flash** for conversations (via Google Gemini API)
- **Gemini 2.5 Pro** for summaries (via Vertex AI)

## 🛡️ Production Deployment

### Security Considerations
1. Use environment variables for all sensitive data
2. Enable HTTPS/SSL in production
3. Restrict CORS origins in `app.py` for production
4. Use a proper session store (Redis/Database) instead of in-memory storage

### Performance
- The application is stateless except for session data
- Consider using a load balancer for multiple instances
- Monitor API usage for Google Cloud services

## 🧪 Testing

### Debug Interface
Visit `http://localhost:8000/debug` to access testing tools:
- Create test sessions
- Preview AI outputs
- Test PDF generation

### API Endpoints
- `GET /` - Landing page
- `GET /chat` - Chat interface
- `POST /api/chat` - Chat API
- `GET /api/summary/{session_id}` - Generate summary
- `POST /api/send-summary` - Send PDF to doctor

## 📞 Support

For technical issues:
1. Check the console output for error messages
2. Verify environment variables are set correctly
3. Ensure Google Cloud authentication is working
4. Test email functionality separately

## 📚 **Helpful Files for Deployment**

| File | Purpose | When to Use |
|------|---------|-------------|
| `MY_CREDENTIALS.txt` | CJ's actual credentials | **Start here** - for immediate deployment |
| `CREDENTIAL_SWITCHING_GUIDE.md` | Step-by-step switching guide | When switching to lab credentials |
| `CREDENTIALS_TEMPLATE.txt` | Template for new credentials | Reference for credential format |
| `PDF_MANAGEMENT.md` | PDF handling explanation | Understanding PDF behavior |
| `SECURITY_SETUP.md` | Security best practices | Production deployment guidance |

**📖 Start with: `MY_CREDENTIALS.txt` → Use: `CREDENTIAL_SWITCHING_GUIDE.md` later**

---

## 🔄 Updates

To update the application:
1. Replace files in this directory
2. Run `pip install -r requirements.txt` to update dependencies
3. Restart the application
