# PowerShell script to activate myenv virtual environment
Write-Host "Activating myenv virtual environment..." -ForegroundColor Green

# Activate the virtual environment
& ".\myenv\Scripts\Activate.ps1"

Write-Host "Virtual environment activated!" -ForegroundColor Green
Write-Host ""
Write-Host "To run the application:" -ForegroundColor Yellow
Write-Host "  Flask API: python app.py" -ForegroundColor White
Write-Host "  Streamlit:  streamlit run app.py" -ForegroundColor White
Write-Host ""
Write-Host "To deactivate, type: deactivate" -ForegroundColor Cyan