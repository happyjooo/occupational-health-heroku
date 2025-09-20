# 📄 PDF File Management

## 🔍 **How PDFs Work in This Application**

### **Current Behavior**:
1. **PDF Generation**: When a summary is sent to a doctor, a PDF is temporarily created
2. **Email Attachment**: The PDF is attached to the email 
3. **Automatic Cleanup**: After successful email send, the PDF is deleted
4. **Storage Location**: Temporary PDFs are stored in `temp_pdfs/` directory

## 📁 **File Structure**

```
deployment_package/
├── temp_pdfs/                    # Temporary PDF storage
│   └── occupational_health_analysis_[session]_[timestamp].pdf
└── app.py                        # Main application
```

## 🗑️ **Cleanup Behavior**

### **Successful Email Send**:
- ✅ PDF is created
- ✅ Email is sent with PDF attachment
- ✅ PDF file is automatically deleted
- ✅ No storage accumulation

### **Failed Email Send**:
- ⚠️ PDF remains in `temp_pdfs/` folder
- ⚠️ Manual cleanup may be needed
- ⚠️ Files will accumulate if email is not configured

## 🚀 **Deployment Considerations**

### **Local Development**:
- PDFs stored in `temp_pdfs/` directory
- Files cleaned up after successful sends
- Failed sends leave files for debugging

### **Cloud Deployment** (Heroku, Railway, Vercel):
- **Ephemeral Storage**: Files may be lost on server restart
- **Storage Limits**: Some platforms have disk space limits
- **Automatic Cleanup**: Files deleted after email send prevents accumulation

### **Container Deployment** (Docker):
- PDFs stored in container's temporary directory
- Files lost when container restarts
- Consider mounting temp volume if persistence needed

## 🛠️ **Manual Cleanup**

If PDFs accumulate due to email issues:

```bash
# Remove all temporary PDFs
rm -rf temp_pdfs/

# Or remove PDFs older than 1 day
find temp_pdfs/ -name "*.pdf" -mtime +1 -delete
```

## 🔧 **Configuration Options**

### **Environment Variables**:
- `SMTP_USERNAME` and `EMAIL_PASSWORD` must be set for automatic cleanup
- Without email config, PDFs will accumulate in `temp_pdfs/`

### **Storage Location**:
The temp directory can be customized by modifying `app.py`:
```python
temp_dir = "temp_pdfs"  # Change this to custom location
```

## 📊 **Monitoring**

### **What to Monitor**:
1. **Disk Usage**: Check `temp_pdfs/` directory size
2. **Email Success Rate**: Monitor email send success/failure
3. **File Accumulation**: Watch for growing PDF count

### **Logs to Watch**:
```
✅ Email sent successfully to doctor@example.com
🗑️ Temporary PDF file cleaned up
⚠️ Email sending failed, but PDF was generated
⚠️ PDF will remain in temp_pdfs/ until email is configured
```

## 🚨 **Troubleshooting**

### **PDFs Accumulating**:
1. Check email configuration
2. Verify SMTP credentials
3. Test email connectivity
4. Monitor temp_pdfs/ directory

### **Storage Full**:
1. Clear temp_pdfs/ directory
2. Fix email configuration
3. Restart application

### **PDFs Missing**:
- Normal behavior if email sent successfully
- Check email sent logs
- Verify recipient received email

## 💡 **Best Practices**

1. **Monitor Storage**: Set up alerts for disk usage
2. **Email Testing**: Test email configuration regularly  
3. **Backup Strategy**: Don't rely on temp PDFs for persistence
4. **Log Monitoring**: Watch for email send failures
5. **Cleanup Schedule**: Consider periodic cleanup scripts for production
