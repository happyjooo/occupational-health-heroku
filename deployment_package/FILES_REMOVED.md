# 📁 Files Removed from Original Project

This document lists all files that were **NOT** included in the deployment package.
These files can be safely deleted from the original project if you want to clean it up.

## 🧪 Testing & Demo Files
```
ai_patient_demo.py
test_demo.py
ui_demo_helper.py
web_ui_demo.py
test_checkpoints.py
start_demo.sh
tests/
  ├── fast_test.py
  ├── simple_test.py
  ├── test_2_agent_conversation.py
  ├── test_vertex_ai.py
  └── test_web_app.py
```

## 📊 Evaluation System (Separate from main app)
```
langgraph_evaluation/
  ├── All files and subdirectories
  └── (This is a complete separate system)
```

## 📚 Extra Documentation
```
AI_PATIENT_DEMO_README.md
EMAIL_SETUP_INSTRUCTIONS.md
INTEGRATED_SYSTEM_README.md
evaluation_prd.txt
prd.md
summary_report_complex_multi_exposure.md
email_requirements.txt
```

## 🔧 Redundant/Legacy Files
```
main.py
start_integrated_system.py
start_server.py
package-lock.json
```

## 🏗️ Build Artifacts
```
__pycache__/ (all directories)
venv/
*.pyc files
```

## ⚠️ **IMPORTANT**: Files You MUST Keep
The following files are **ESSENTIAL** and are included in the deployment package:
- `app.py` - Main application
- `src/` - Core application logic
- `html_version/` - Frontend interface
- `multi_agent_prompt/` & `patient_prompt/` - AI prompts
- `manual_table_converter.py` - PDF generation
- `requirements.txt` - Dependencies
- `README.md` - Main documentation

## 🧹 Cleanup Commands
To remove all non-essential files from your original project:

```bash
# Remove demo/test files
rm -f ai_patient_demo.py test_demo.py ui_demo_helper.py web_ui_demo.py test_checkpoints.py start_demo.sh
rm -f main.py start_integrated_system.py start_server.py package-lock.json
rm -f AI_PATIENT_DEMO_README.md EMAIL_SETUP_INSTRUCTIONS.md INTEGRATED_SYSTEM_README.md
rm -f evaluation_prd.txt prd.md summary_report_complex_multi_exposure.md email_requirements.txt

# Remove directories
rm -rf tests/
rm -rf langgraph_evaluation/
rm -rf venv/

# Remove build artifacts
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
```

**Total files removed**: ~150+ files and directories
**Deployment package size**: 296KB (32 essential files)
**Original project size**: Much larger with all test/demo files

