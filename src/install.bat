@echo off
"python-3.13.5-amd64.exe"
if %errorlevel% neq 0 (
    echo Installation failed with error code %errorlevel%.
    exit /b %errorlevel%
)
echo Python 3.13.5 installed successfully.
REM Set environment variables
setx PATH "%PATH%;C:\Python313\Scripts;C:\Python313"
setx PYTHONPATH "C:\Python313\Lib;C:\Python313\DLLs"
REM Verify installation
python --version
"tesseract-ocr-w64-setup-5.5.0.20241111.exe"
if %errorlevel% neq 0 (
    echo Tesseract OCR installation failed with error code %errorlevel%.
    exit /b %errorlevel%
)
echo Tesseract OCR installed successfully.
REM Set Tesseract OCR environment variable

"pip install python-dotenv selenium pillow pytesseract webdriver-manager opencv-python transformers torch torchvision nltk"