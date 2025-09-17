# Doc to Markdown Converter - PowerShell Setup Script
# This script sets up the environment and runs the converter on Windows

param(
    [string]$InputFile = "",
    [string]$InputDir = "",
    [string]$OutputDir = "",
    [switch]$Help,
    [switch]$Setup,
    [switch]$Test
)

$ErrorActionPreference = "Stop"

function Write-Header {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Doc to Markdown Converter for RAG" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

function Test-PythonInstallation {
    Write-Host "Checking Python installation..." -ForegroundColor Yellow
    
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            
            if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
                Write-Host "❌ Python 3.8+ required. Current: $pythonVersion" -ForegroundColor Red
                return $false
            }
            
            Write-Host "✓ Python OK: $pythonVersion" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Could not determine Python version" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Python not found. Please install Python 3.8+ and add to PATH" -ForegroundColor Red
        Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
        return $false
    }
}

function Install-Dependencies {
    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
    
    if (Test-Path "requirements.txt") {
        try {
            python -m pip install -r requirements.txt
            Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
            return $true
        } catch {
            Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
            return $false
        }
    } else {
        Write-Host "❌ requirements.txt not found" -ForegroundColor Red
        return $false
    }
}

function Test-Installation {
    Write-Host "Testing installation..." -ForegroundColor Yellow
    
    try {
        python setup.py
        Write-Host "✓ Installation test completed" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ Installation test failed" -ForegroundColor Red
        return $false
    }
}

function Show-Help {
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\convert_docs.ps1 -Setup                    # Set up environment"
    Write-Host "  .\convert_docs.ps1 -Test                     # Test installation"
    Write-Host "  .\convert_docs.ps1 -InputFile file.html     # Convert single file"
    Write-Host "  .\convert_docs.ps1 -InputDir docs\          # Convert directory"
    Write-Host "  .\convert_docs.ps1 -Help                     # Show this help"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\convert_docs.ps1 -InputFile 'confluence_export.html'"
    Write-Host "  .\convert_docs.ps1 -InputDir 'Documents\' -OutputDir 'Markdown\'"
    Write-Host ""
    Write-Host "Direct Python usage:" -ForegroundColor Yellow
    Write-Host "  python doc_to_markdown_converter.py input.html"
    Write-Host "  python doc_to_markdown_converter.py -d documents\ -od markdown\"
}

function Convert-SingleFile {
    param([string]$File, [string]$Output)
    
    if (-not (Test-Path $File)) {
        Write-Host "❌ File not found: $File" -ForegroundColor Red
        return
    }
    
    Write-Host "Converting: $File" -ForegroundColor Yellow
    
    try {
        if ($Output) {
            python doc_to_markdown_converter.py $File -o $Output
        } else {
            python doc_to_markdown_converter.py $File
        }
        Write-Host "✓ Conversion completed successfully" -ForegroundColor Green
    } catch {
        Write-Host "❌ Conversion failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Convert-Directory {
    param([string]$InputDirectory, [string]$OutputDirectory)
    
    if (-not (Test-Path $InputDirectory)) {
        Write-Host "❌ Directory not found: $InputDirectory" -ForegroundColor Red
        return
    }
    
    Write-Host "Converting directory: $InputDirectory" -ForegroundColor Yellow
    
    try {
        if ($OutputDirectory) {
            python doc_to_markdown_converter.py -d $InputDirectory -od $OutputDirectory
        } else {
            python doc_to_markdown_converter.py -d $InputDirectory
        }
        Write-Host "✓ Directory conversion completed successfully" -ForegroundColor Green
    } catch {
        Write-Host "❌ Directory conversion failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Main {
    Write-Header
    
    if ($Help) {
        Show-Help
        return
    }
    
    if ($Setup) {
        Write-Host "Setting up Doc to Markdown Converter..." -ForegroundColor Yellow
        
        if (-not (Test-PythonInstallation)) {
            return
        }
        
        if (-not (Install-Dependencies)) {
            return
        }
        
        Write-Host "✓ Setup completed successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Try running:" -ForegroundColor Yellow
        Write-Host "  .\convert_docs.ps1 -Test"
        return
    }
    
    if ($Test) {
        if (-not (Test-PythonInstallation)) {
            return
        }
        
        Test-Installation
        return
    }
    
    # Check if converter script exists
    if (-not (Test-Path "doc_to_markdown_converter.py")) {
        Write-Host "❌ doc_to_markdown_converter.py not found in current directory" -ForegroundColor Red
        Write-Host "Please ensure you're in the correct directory with all script files" -ForegroundColor Yellow
        return
    }
    
    if ($InputFile) {
        Convert-SingleFile -File $InputFile -Output $OutputDir
    } elseif ($InputDir) {
        Convert-Directory -InputDirectory $InputDir -OutputDirectory $OutputDir
    } else {
        Write-Host "No input specified. Use -Help for usage information." -ForegroundColor Yellow
        Write-Host ""
        
        # Interactive mode
        Write-Host "Interactive Mode:" -ForegroundColor Cyan
        Write-Host "1. Convert single file"
        Write-Host "2. Convert directory"
        Write-Host "3. Show help"
        Write-Host "4. Exit"
        Write-Host ""
        
        $choice = Read-Host "Choose an option (1-4)"
        
        switch ($choice) {
            "1" {
                $file = Read-Host "Enter path to file"
                $output = Read-Host "Enter output path (or press Enter for default)"
                if ($output -eq "") { $output = $null }
                Convert-SingleFile -File $file -Output $output
            }
            "2" {
                $inputDir = Read-Host "Enter input directory path"
                $outputDir = Read-Host "Enter output directory path (or press Enter for default)"
                if ($outputDir -eq "") { $outputDir = $null }
                Convert-Directory -InputDirectory $inputDir -OutputDirectory $outputDir
            }
            "3" {
                Show-Help
            }
            "4" {
                Write-Host "Goodbye!" -ForegroundColor Green
                return
            }
            default {
                Write-Host "Invalid choice" -ForegroundColor Red
            }
        }
    }
}

# Run main function
Main
