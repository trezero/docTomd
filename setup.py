#!/usr/bin/env python3
"""
Quick setup script for the Doc to Markdown Converter
This script checks dependencies and sets up the environment
"""

import sys
import subprocess
import importlib
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is adequate."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✓ Python version OK: {version.major}.{version.minor}.{version.micro}")
    return True

def check_pip():
    """Check if pip is available."""
    try:
        import pip
        print("✓ pip is available")
        return True
    except ImportError:
        print("❌ pip not found. Please install pip first.")
        return False

def install_package(package_name):
    """Install a package using pip."""
    try:
        print(f"Installing {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package_name}")
        return False

def check_and_install_dependencies():
    """Check and install required dependencies."""
    required_packages = [
        ('bs4', 'beautifulsoup4'),
        ('html2text', 'html2text'),
        ('docx', 'python-docx'),
        ('markdownify', 'markdownify'),
        ('mammoth', 'mammoth'),
        ('lxml', 'lxml')
    ]
    
    missing_packages = []
    
    print("\nChecking dependencies...")
    
    for import_name, package_name in required_packages:
        try:
            importlib.import_module(import_name)
            print(f"✓ {package_name}")
        except ImportError:
            print(f"❌ {package_name} (missing)")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\nInstalling missing packages: {', '.join(missing_packages)}")
        
        # Try to install from requirements.txt first
        if Path('requirements.txt').exists():
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
                print("✓ Installed packages from requirements.txt")
                return True
            except subprocess.CalledProcessError:
                print("❌ Failed to install from requirements.txt, trying individual packages...")
        
        # Install packages individually
        success = True
        for package in missing_packages:
            if not install_package(package):
                success = False
        
        return success
    else:
        print("✓ All dependencies are installed")
        return True

def test_installation():
    """Test the installation by importing the main module."""
    try:
        print("\nTesting installation...")
        
        # Try to import the main converter
        sys.path.insert(0, str(Path(__file__).parent))
        
        from doc_to_markdown_converter import DocToMarkdownConverter
        
        # Create a simple test
        converter = DocToMarkdownConverter()
        print("✓ DocToMarkdownConverter imported successfully")
        
        # Test basic functionality
        test_html = "<html><body><h1>Test</h1><p>This is a test.</p></body></html>"
        result = converter.convert_html_to_markdown(test_html)
        
        if "# Test" in result and "This is a test" in result:
            print("✓ Basic conversion test passed")
            return True
        else:
            print("❌ Basic conversion test failed")
            return False
            
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def create_sample_files():
    """Create sample files for testing."""
    print("\nCreating sample files...")
    
    # Create a simple test HTML file
    sample_html = """<!DOCTYPE html>
<html>
<head>
    <title>Sample Document</title>
</head>
<body>
    <h1>Sample Document</h1>
    <p><strong>Date:</strong> September 17, 2025</p>
    <h2>Introduction</h2>
    <p>This is a sample document for testing the doc to markdown converter.</p>
    <h2>Features</h2>
    <ul>
        <li>Converts HTML to Markdown</li>
        <li>Handles various document formats</li>
        <li>Optimized for RAG workflows</li>
    </ul>
    <h2>System Requirements</h2>
    <p>The following are required:</p>
    <ul>
        <li>Python 3.8+</li>
        <li>Required packages (see requirements.txt)</li>
    </ul>
</body>
</html>"""
    
    try:
        with open('sample_document.html', 'w', encoding='utf-8') as f:
            f.write(sample_html)
        print("✓ Created sample_document.html")
        return True
    except Exception as e:
        print(f"❌ Failed to create sample files: {e}")
        return False

def show_next_steps():
    """Show next steps after successful setup."""
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Test with the sample file:")
    print("   python doc_to_markdown_converter.py sample_document.html")
    print()
    print("2. Convert your own files:")
    print("   python doc_to_markdown_converter.py your_file.html")
    print()
    print("3. Batch convert a directory:")
    print("   python doc_to_markdown_converter.py -d your_directory/")
    print()
    print("4. Run the example script:")
    print("   python example_usage.py")
    print()
    print("5. Use the Windows batch script:")
    print("   Double-click convert_docs.bat")
    print()
    print("For more information, see README.md")
    print("=" * 60)

def main():
    """Main setup function."""
    print("Doc to Markdown Converter - Setup Script")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_pip():
        sys.exit(1)
    
    # Install dependencies
    if not check_and_install_dependencies():
        print("\n❌ Failed to install all dependencies")
        sys.exit(1)
    
    # Test installation
    if not test_installation():
        print("\n❌ Installation test failed")
        sys.exit(1)
    
    # Create sample files
    create_sample_files()
    
    # Show next steps
    show_next_steps()

if __name__ == "__main__":
    main()
