@echo off
REM Doc to Markdown Converter - Windows Batch Script
REM This script helps you quickly convert documents to markdown format

echo ===============================================
echo Document to Markdown Converter for RAG
echo ===============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
python -c "import bs4, html2text, docx, markdownify, mammoth" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo Dependencies OK!
echo.

REM Get user input
if "%~1"=="" (
    echo Usage Options:
    echo 1. Single file conversion
    echo 2. Batch directory conversion
    echo 3. Show help
    echo.
    set /p choice="Enter choice (1-3): "
    
    if "!choice!"=="1" goto single_file
    if "!choice!"=="2" goto batch_convert
    if "!choice!"=="3" goto show_help
    goto show_help
) else (
    REM Command line argument provided
    python doc_to_markdown_converter.py %*
    goto end
)

:single_file
echo.
echo Single File Conversion
echo =====================
set /p input_file="Enter path to input file: "
if not exist "%input_file%" (
    echo ERROR: File not found: %input_file%
    pause
    exit /b 1
)

set /p output_file="Enter output path (or press Enter for default): "
if "%output_file%"=="" (
    python doc_to_markdown_converter.py "%input_file%"
) else (
    python doc_to_markdown_converter.py "%input_file%" -o "%output_file%"
)
goto end

:batch_convert
echo.
echo Batch Directory Conversion
echo ==========================
set /p input_dir="Enter input directory path: "
if not exist "%input_dir%" (
    echo ERROR: Directory not found: %input_dir%
    pause
    exit /b 1
)

set /p output_dir="Enter output directory (or press Enter for default): "
set /p pattern="Enter file pattern (or press Enter for all files): "

if "%pattern%"=="" set pattern=*.*

if "%output_dir%"=="" (
    python doc_to_markdown_converter.py -d "%input_dir%" --pattern "%pattern%"
) else (
    python doc_to_markdown_converter.py -d "%input_dir%" -od "%output_dir%" --pattern "%pattern%"
)
goto end

:show_help
python doc_to_markdown_converter.py --help
goto end

:end
echo.
echo Conversion complete!
pause
