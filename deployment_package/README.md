# 🚀 Occupational History AI - Deployment Package

**Ready-to-deploy package with all essential files and credentials for immediate deployment.**

## 🎯 **Quick Start (5 minutes)**

1. **📋 Prerequisites**: Python 3.9+
2. **📦 Install**: `pip install -r requirements.txt`
3. **🔐 Credentials**: Look at `MY_CREDENTIALS.txt` for CJ's working credentials
4. **⚡ Run**: Copy export commands and run `python app.py`
5. **✅ Test**: Visit `http://localhost:8000` and `http://localhost:8000/debug`

**🎉 That's it! The app works immediately with provided credentials.**

---

## 📁 **What's Included**

### 🚀 **Core Application**
- `app.py` - Main FastAPI application
- `requirements.txt` - Python dependencies
- `html_version/` - Frontend web interface
- `src/` - Core application logic
- `manual_table_converter.py` - PDF generation

### 📖 **Documentation & Guides**
- `DEPLOYMENT_GUIDE.md` - **Main deployment instructions**
- `CREDENTIAL_SWITCHING_GUIDE.md` - **How to switch to lab credentials**
- `PDF_MANAGEMENT.md` - PDF handling explanation
- `SECURITY_SETUP.md` - Security best practices

### 🔐 **Credential Files**
- `MY_CREDENTIALS.txt` - **CJ's working credentials (start here)**
- `CREDENTIALS_TEMPLATE.txt` - Template for new credentials

### 🤖 **AI Prompts**
- `multi_agent_prompt/` - AI system prompts
- `patient_prompt/` - Patient persona prompts

---

## 🏁 **Deployment Phases**

### **Phase 1: Immediate Deployment** ⚡
- Use CJ's credentials from `MY_CREDENTIALS.txt`
- No setup required - works immediately
- Perfect for testing and initial deployment

### **Phase 2: Lab Credentials** 🏥
- Switch to lab's own Google Cloud + Gmail
- Follow `CREDENTIAL_SWITCHING_GUIDE.md`
- 5-minute switching process when ready

---

## 🎮 **What You Can Do**

### 👥 **Patient Simulation**
- Chat with AI patients (Arthur, Eleanor, Leo)
- Realistic occupational health scenarios
- Natural conversation flow

### 📊 **AI Summary Generation**
- Professional medical summaries
- Structured exposure tables
- Doctor-ready format

### 📧 **Email Integration**  
- Send PDF reports to doctors
- Dr Ryan (`ryan.hoy@monash.edu`)
- Chun Joo (CJ) (`gohchunjoo000@gmail.com`)

### 🧪 **Debug Interface**
- Test all features
- Preview outputs
- Troubleshoot issues

---

## 📞 **Support**

1. **📖 Read**: `DEPLOYMENT_GUIDE.md` for main instructions
2. **🔄 Switch**: `CREDENTIAL_SWITCHING_GUIDE.md` for credential changes  
3. **🛡️ Security**: `SECURITY_SETUP.md` for production setup
4. **📄 PDFs**: `PDF_MANAGEMENT.md` for PDF behavior

---

## 🛡️ **Security Notes**

- ✅ Credentials use environment variables (secure)
- ✅ No hardcoded secrets in code
- ✅ Temporary PDF cleanup after email send
- ⚠️ Keep `MY_CREDENTIALS.txt` private
- ⚠️ Don't commit real credentials to git

---

## 🚀 **Ready to Deploy?**

**👀 Look at: `MY_CREDENTIALS.txt`** 

**📖 Follow: `DEPLOYMENT_GUIDE.md`**

**🎉 Get running in 5 minutes!**