# Quick Testing Instructions

## ❌ What You Tried (Wrong):
```bash
python https://huggingface.co/spaces/karan-01/learningagent
```
This is incorrect because:
- `https://huggingface.co/spaces/karan-01/learningagent` is a WEB URL, not a Python file
- You can't run URLs as Python programs

## ✅ What You Should Do:

### 1. Check Your Deployed Space:
- Go to: https://huggingface.co/spaces/karan-01/learningagent
- This shows your Space dashboard, logs, and documentation
- Your API is actually at: `https://karan-01-learningagent.hf.space`

### 2. Test API with curl (Easy):
```bash
# Test health check
curl https://karan-01-learningagent.hf.space/

# Register a learner
curl -X POST https://karan-01-learningagent.hf.space/api/learner/register \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "age": 25, "gender": "male", "learning_style": "visual", "preferences": ["algorithms"]}'

# Get all learners
curl https://karan-01-learningagent.hf.space/api/learners
```

### 3. Test API with Python Script:
```bash
pip install requests
python test_api.py
```

### 4. Test in Browser:
Simply visit: https://karan-01-learningagent.hf.space/
This should show: `{"message": "Welcome to the Learning Agent API"}`

## 🔧 If Your Space Isn't Working:

### Check Build Status:
1. Go to https://huggingface.co/spaces/karan-01/learningagent
2. Look for "Build logs" tab
3. See if build failed or succeeded

### Common Issues:
- Build failing → Check requirements.txt syntax
- Space not starting → Check app.py for errors
- API not responding → Check PORT configuration

### Fix Build Issues:
If build fails, check:
1. All files are uploaded correctly
2. requirements.txt is valid
3. All imports exist
4. Environment variables are set