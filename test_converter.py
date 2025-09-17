#!/usr/bin/env python3
"""
Test script for the Doc to Markdown Converter
Demonstrates usage with the provided Confluence export example (.doc extension)
"""

import tempfile
import os
from pathlib import Path
from doc_to_markdown_converter import DocToMarkdownConverter

def create_test_confluence_file():
    """Create a test file similar to the provided Confluence export with .doc extension."""
    confluence_content = """Date: Wed, 17 Sep 2025 15:33:16 +0000 (UTC)
Message-ID: <265945599.29.1758123196242@4bdbc70beb76>
Subject: Exported From Confluence
MIME-Version: 1.0
Content-Type: multipart/related; 
	boundary="----=_Part_28_2131790293.1758123196241"

------=_Part_28_2131790293.1758123196241
Content-Type: text/html; charset=UTF-8
Content-Transfer-Encoding: quoted-printable

<html>
<head>
    <title>AI+ 2.0 Release Notes</title>
</head>
<body>
    <h1>AI+ 2.0 Release Notes</h1>
    <div class="Section1">
        <p><strong>Release Date:</strong> June 2024</p>
        <p><strong>Bundle Name:</strong> AI+ 2.0 OnPrem Suite</p>
        <hr>
        <h4 id="AI+2.0ReleaseNotes-Purpose">Purpose</h4>
        <p>This release introduces AI+ 2.0, a comprehensive suite of onPrem AI features designed for seamless integration with SWARM, OM, and iconik. AI+ 2.0 offers advanced capabilities in media management, including transcription, summarization, translation, facial recognition, and object recognition. This bundle aims to enhance operational efficiency and media content management with robust, localized AI solutions.</p>
        
        <h4 id="AI+2.0ReleaseNotes-What's-New">What's New in AI+ 2.0?</h4>
        <ul>
            <li><strong>Advanced Transcription:</strong> Automatically transcribe and generate robust metadata values in multiple languages for any number of metadata fields across all of an organization's media content. (Now able to be run 100% on prem with no $/sec required for OpenAI anymore.)</li>
            <li><strong>AutoTranslation:</strong> Translate the spoken audio of selected media content into multiple languages. AutoTranslation supports over 20 languages, enabling broader content accessibility.</li>
            <li><strong>Facial Recognition:</strong> Identify and tag individuals within your media library based on a simple training process which can occur directly within iconik or through our APIs.</li>
            <li><strong>Robust Object Detection:</strong> Go beyond Object Detection to Object Recognition where we combine the power of standard Object Detection models with Vision based models to find specific objects within media files. Instead of just being able to find a car, find the Ford F-150 for example. All with no traditional object detection training required.</li>
        </ul>
        
        <h4 id="AI+2.0ReleaseNotes-SystemRequirements">System Requirements</h4>
        <p>To fully leverage the capabilities of AI+ 2.0, the following system specifications are required:</p>
        
        <h3 id="AI+2.0ReleaseNotes-CPU">CPU</h3>
        <ul>
            <li>Processor: Intel Xeon or AMD EPYC series</li>
            <li>Cores: Minimum 16 cores (32 threads)</li>
            <li>Clock Speed: Base clock speed of 2.6 GHz or higher</li>
        </ul>
        
        <h3 id="AI+2.0ReleaseNotes-Memory">Memory (RAM)</h3>
        <ul>
            <li>Minimum: 128 GB</li>
            <li>Recommended: 256 GB or higher for better performance and handling large datasets</li>
        </ul>
    </div>
</body>
</html>
------=_Part_28_2131790293.1758123196241--
"""
    
    # Create temporary file with .doc extension to match real Confluence exports
    with tempfile.NamedTemporaryFile(mode='w', suffix='.doc', delete=False, encoding='utf-8') as f:
        f.write(confluence_content)
        return f.name

def test_converter():
    """Test the converter with the Confluence export example (.doc file)."""
    print("Testing Doc to Markdown Converter")
    print("=" * 50)
    print("Testing Confluence .doc export handling")
    print("=" * 50)
    
    # Create test file
    test_file = create_test_confluence_file()
    print(f"✓ Created test Confluence .doc file: {test_file}")
    
    try:
        # Initialize converter
        converter = DocToMarkdownConverter({
            'ignore_images': True,
            'ignore_links': False,
            'body_width': 0
        })
        
        # Convert the file
        output_file = test_file.replace('.doc', '_converted.md')
        result = converter.convert_file(test_file, output_file)
        
        print(f"✓ Converted to: {result}")
        
        # Read and display the result
        with open(result, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("\n" + "=" * 50)
        print("CONVERTED MARKDOWN CONTENT:")
        print("=" * 50)
        print(content[:2000])  # Show first 2000 characters
        if len(content) > 2000:
            print(f"\n... (truncated, total length: {len(content)} characters)")
        print("=" * 50)
        
        # Show file info
        original_size = os.path.getsize(test_file)
        converted_size = os.path.getsize(result)
        
        print(f"\nFile Conversion Summary:")
        print(f"Original (.doc):     {original_size:,} bytes")
        print(f"Converted (.md):     {converted_size:,} bytes")
        print(f"Size change:         {((converted_size - original_size) / original_size * 100):+.1f}%")
        
        # Verify content extraction
        if "AI+ 2.0 Release Notes" in content and "Advanced Transcription" in content:
            print("✅ Content extraction successful!")
            print("✅ Confluence .doc export handling working correctly!")
        else:
            print("❌ Content extraction may have issues")
        
        # Clean up
        os.unlink(test_file)
        print(f"\n✓ Test file cleaned up: {test_file}")
        print(f"✓ Output saved for inspection: {result}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        if os.path.exists(test_file):
            os.unlink(test_file)

if __name__ == "__main__":
    test_converter()
