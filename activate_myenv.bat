@echo off
echo Activating myenv virtual environment...
call myenv\Scripts\activate.bat
echo Virtual environment activated!
echo.
echo To run the application:
echo python app.py
echo.
echo Or for Streamlit app:
echo streamlit run app.py
echo.
echo To deactivate, type: deactivate