# Learning Agent - Virtual Environment Setup

## Virtual Environment: myenv

This project now includes a virtual environment named `myenv` for isolated Python dependencies.

### Quick Start

1. **Activate the virtual environment:**
   ```bash
   # Windows Command Prompt
   activate_myenv.bat

   # Windows PowerShell (Method 1 - Recommended)
   powershell -ExecutionPolicy Bypass -File activate_myenv.ps1

   # Windows PowerShell (Method 2 - Manual)
   .\myenv\Scripts\Activate.ps1

   # Or manually:
   # Command Prompt: myenv\Scripts\activate
   # PowerShell: .\myenv\Scripts\Activate.ps1
   ```

2. **Run the application:**
   ```bash
   # Streamlit Learning Agent Dashboard (Main Application)
   streamlit run app.py

   # Note: This is a Streamlit app, not a Flask API
   ```

3. **Deactivate when done:**
   ```bash
   deactivate
   ```

### Environment Configuration

- **Database:** MongoDB Atlas (configured in `.env`)
- **Dependencies:** Listed in `requirements.txt`
- **Environment variables:** Configured in `.env`

### Key Features

- ✅ Fixed Engagement model attribute access errors
- ✅ MongoDB Atlas integration
- ✅ Isolated virtual environment
- ✅ Comprehensive scoring system
- ✅ AI-powered recommendations (local fallback)

### Troubleshooting

If you encounter import errors:
1. Ensure virtual environment is activated
2. Check that dependencies are installed: `pip list`
3. Verify `.env` configuration

### Database Setup

The application uses MongoDB Atlas. Update the connection string in `.env`:
```env
MONGO_URI=mongodb+srv://your-connection-string
MONGO_DB=learning_agent_db