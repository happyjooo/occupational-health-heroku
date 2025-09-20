# 🔄 Easy Credential Switching Guide

## 🎯 **Current Situation**
- **Phase 1**: Using CJ's credentials for initial deployment
- **Phase 2**: Switch to lab's credentials when ready

## 🚀 **Phase 1: Using CJ's Credentials (Now)**

### ✅ **What You Have**:
- ✅ `MY_CREDENTIALS.txt` with CJ's actual credentials filled in
- ✅ Working application with immediate email + AI functionality
- ✅ No need to set up Google Cloud or Gmail initially

### 📋 **Your Steps**:
1. Open `MY_CREDENTIALS.txt` 
2. Copy the `export` commands with CJ's real values
3. Run them in terminal
4. Run `python app.py`
5. Test at `http://localhost:8000/debug`

---

## 🏥 **Phase 2: Switching to Lab Credentials (Later)**

### 🔧 **What Lab Needs to Prepare**:

**🔹 Google Cloud Setup**:
1. Create new Google Cloud project
2. Enable Vertex AI API + Generative AI API  
3. Note the project ID

**🔹 Gmail Setup**:
1. Use lab's Gmail account
2. Enable 2-factor authentication
3. Generate App Password for "Mail"
4. Note the 16-character password

### 🔄 **Switching Process (5 minutes)**:

**Step 1: Update Credentials File**
```bash
# Edit MY_CREDENTIALS.txt with lab's values:
GOOGLE_CLOUD_PROJECT=lab-project-id-here
SMTP_USERNAME=lab-email@domain.com
EMAIL_PASSWORD=lab-16-char-password
```

**Step 2: Apply New Credentials**
```bash
# Copy the updated export commands from MY_CREDENTIALS.txt
export GOOGLE_CLOUD_PROJECT="lab-project-id-here"
export SMTP_USERNAME="lab-email@domain.com"
export EMAIL_PASSWORD="lab-16-char-password"
```

**Step 3: Restart Application**
```bash
# Stop current server (Ctrl+C)
python app.py
```

**Step 4: Verify Switch Worked**
```bash
# Check credentials are set:
echo "Project: $GOOGLE_CLOUD_PROJECT"
echo "Email: $SMTP_USERNAME" 
echo "Password Set: $(if [ -n "$EMAIL_PASSWORD" ]; then echo 'YES'; else echo 'NO'; fi)"

# Test application:
# Visit: http://localhost:8000/debug
# Try generating and sending a summary
```

---

## 🛡️ **Security Notes**

### ✅ **Good Practices**:
- Keep `MY_CREDENTIALS.txt` private and secure
- Use environment variables (never hardcode in code)
- Change passwords if compromised
- Delete old credential files when no longer needed

### ⚠️ **Important**:
- Never commit real credentials to git
- Both credential sets will work independently
- No conflicts between CJ's and lab's setups
- Each uses their own Google Cloud billing

---

## 🧪 **Testing After Switch**

### 🔍 **What to Test**:
1. **Chat Interface**: Start new conversation
2. **AI Summary**: Generate patient summary  
3. **Email Sending**: Send PDF to doctor
4. **PDF Generation**: Check PDF quality

### 🚨 **Troubleshooting**:

**❌ Email Not Working**:
```bash
# Check email password is set:
echo $EMAIL_PASSWORD
# Should show 16-character password, not empty

# Re-export if needed:
export EMAIL_PASSWORD="correct-16-char-password"
```

**❌ AI Not Working**:
```bash
# Check project ID:
echo $GOOGLE_CLOUD_PROJECT
# Should match lab's project ID

# Check Google Cloud authentication:
gcloud auth application-default login
```

**❌ Authentication Issues**:
```bash
# For lab deployment, authenticate with lab account:
gcloud auth application-default login
# Or set service account key:
export GOOGLE_APPLICATION_CREDENTIALS="path/to/lab-service-key.json"
```

---

## 📞 **Quick Reference**

### 🔧 **Current Credentials** (Phase 1):
- **Project**: CJ's Google Cloud project
- **Email**: CJ's Gmail account  
- **Billing**: Goes to CJ's account

### 🏥 **Lab Credentials** (Phase 2):
- **Project**: Lab's Google Cloud project
- **Email**: Lab's Gmail account
- **Billing**: Goes to lab's account

### 🚀 **Switch Command Summary**:
```bash
# 1. Update MY_CREDENTIALS.txt
# 2. Copy new export commands
# 3. Run them in terminal
# 4. Restart: python app.py
# 5. Test: http://localhost:8000/debug
```

**✅ The switch should take less than 5 minutes!**

