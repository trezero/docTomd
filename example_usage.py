#!/usr/bin/env python3
"""
Example script demonstrating how to convert the provided Confluence export (.doc)
to clean markdown suitable for RAG workflows.
"""

import tempfile
import os
from pathlib import Path

# Create a sample file similar to your Confluence export
def create_sample_confluence_export():
    """Create a sample file matching your Confluence export format (.doc extension)."""
    sample_content = '''Date: Wed, 17 Sep 2025 15:33:16 +0000 (UTC)
Message-ID: <265945599.29.1758123196242@4bdbc70beb76>
Subject: Exported From Confluence
MIME-Version: 1.0
Content-Type: multipart/related; 
	boundary="----=_Part_28_2131790293.1758123196241"

------=_Part_28_2131790293.1758123196241
Content-Type: text/html; charset=UTF-8
Content-Transfer-Encoding: quoted-printable
Content-Location: file:///C:/exported.html

<html xmlns:o=3D'urn:schemas-microsoft-com:office:office'
      xmlns:w=3D'urn:schemas-microsoft-com:office:word'
      xmlns:v=3D'urn:schemas-microsoft-com:vml'
      xmlns=3D'urn:w3-org-ns:HTML'>
<head>
    <meta http-equiv=3D"Content-Type" content=3D"text/html; charset=3Dutf-8=
">
    <title>AI+ 2.0 Release Notes</title>
    <style>
        /* Lots of CSS styles here */
        @page Section1 { size: 8.5in 11.0in; }
        table { border: solid 1px; }
        /* ... more styles ... */
    </style>
</head>
<body>
    <h1>AI+ 2.0 Release Notes</h1>
    <div class=3D"Section1">
        <p><strong>Release Date:</strong> June 2024</p>
<p><strong>Bundle Name:</strong> AI+ 2.0 OnPrem Suite</p>
<hr>
<h4 id=3D"AI+2.0ReleaseNotes-Purpose">Purpose</h4>
<p>This release introduces AI+ 2.0, a comprehensive suite of onPrem AI feat=
ures designed for seamless integration with SWARM, OM, and iconik. AI+ 2.0 =
offers advanced capabilities in media management, including transcription, =
summarization, translation, facial recognition, and object recognition. Thi=
s bundle aims to enhance operational efficiency and media content managemen=
t with robust, localized AI solutions.</p>
<h4 id=3D"AI+2.0ReleaseNotes-What=E2=80=99sNewinAI+2.0?">What=E2=80=99s New=
 in AI+ 2.0?</h4>
<ul>
<li>
<p><strong>Advanced Transcription::</strong> Automatically transcribe and g=
enerate robust metadata values in multiple languages for any number of meta=
data fields across all of an organization=E2=80=99s media content. (Now abl=
e to be run 100% on prem with no $/sec required for OpenAI anymore.)</p></l=
i>
<li>
<p><strong>AutoTranslation:</strong> Translate the spoken audio of selected=
 media content into multiple languages. AutoTranslation supports over 20 la=
nguages, enabling broader content accessibility.</p></li>
<li>
<p><strong>Facial Recognition:</strong> Identify and tag individuals within=
 your media library based on a simple training process which can occur dire=
ctly within iconik or through our APIs.</p></li>
<li>
<p><strong>Robust Object Detection:</strong> <strong>:</strong> Go beyond O=
bject Detection to Object Recognition where we combine the power of standar=
d Object Detection models with Vision based models to find specific objects=
 within media files. Instead of just being able to find a car, find the For=
d F-150 for example. All with no traditional object detection training requ=
ired. =E2=80=8C</p></li>
</ul>
<hr>
<h4 id=3D"AI+2.0ReleaseNotes-SystemRequirements">System Requirements</h4>
<p>To fully leverage the capabilities of AI+ 2.0, the following system spec=
ifications are required:</p>
<h3 id=3D"AI+2.0ReleaseNotes-CPU">CPU</h3>
<ul>
<li>
<p>Processor: Intel Xeon or AMD EPYC series</p></li>
<li>
<p>Cores: Minimum 16 cores (32 threads)</p></li>
<li>
<p>Clock Speed: Base clock speed of 2.6 GHz or higher</p></li>
</ul>
<h3 id=3D"AI+2.0ReleaseNotes-Memory(RAM)">Memory (RAM)</h3>
<ul>
<li>
<p>Minimum: 128 GB</p></li>
<li>
<p>Recommended: 256 GB or higher for better performance and handling large =
datasets</p></li>
</ul>
    </div>
</body>
</html>
------=_Part_28_2131790293.1758123196241--
'''
    
    # Save to temporary file with .doc extension (like real Confluence exports)
    with tempfile.NamedTemporaryFile(mode='w', suffix='_confluence_export.doc', 
                                   delete=False, encoding='utf-8') as f:
        f.write(sample_content)
        return f.name

def run_conversion_example():
    """Run the conversion example."""
    print("Confluence .doc Export to Markdown Conversion Example")
    print("=" * 60)
    print("Demonstrating conversion of .doc files that contain MHTML content")
    print("=" * 60)
    
    # Create sample file
    sample_file = create_sample_confluence_export()
    print(f"✓ Created sample Confluence .doc export: {sample_file}")
    
    # Import and use the converter
    try:
        from doc_to_markdown_converter import DocToMarkdownConverter
        
        # Initialize converter with RAG-optimized settings
        converter = DocToMarkdownConverter({
            'ignore_images': True,      # Remove images for RAG
            'ignore_links': False,      # Keep links for context
            'body_width': 0,           # No line wrapping
        })
        
        # Convert the file
        output_file = sample_file.replace('.doc', '_converted.md')
        result_path = converter.convert_file(sample_file, output_file, add_metadata=True)
        
        print(f"✓ Converted to markdown: {result_path}")
        
        # Display the converted content
        with open(result_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        print("\n" + "=" * 60)
        print("CONVERTED MARKDOWN CONTENT:")
        print("=" * 60)
        print(markdown_content)
        print("=" * 60)
        
        # Show file sizes for comparison
        original_size = os.path.getsize(sample_file)
        converted_size = os.path.getsize(result_path)
        
        print(f"\nFile Size Comparison:")
        print(f"Original .doc file:   {original_size:,} bytes")
        print(f"Converted Markdown:   {converted_size:,} bytes")
        print(f"Size reduction:       {((original_size - converted_size) / original_size * 100):.1f}%")
        
        # Demonstrate RAG-specific benefits
        print(f"\nRAG Optimization Benefits:")
        print(f"✅ Clean structure suitable for vector embeddings")
        print(f"✅ YAML frontmatter for metadata-based filtering")
        print(f"✅ Preserved hierarchical structure for context")
        print(f"✅ Removed styling and formatting artifacts")
        print(f"✅ Consistent markdown formatting")
        print(f"✅ Automatic detection of MHTML content in .doc files")
        
        # Keep files for inspection
        print(f"\nFiles saved for your inspection:")
        print(f"- Original: {sample_file}")
        print(f"- Converted: {result_path}")
        print(f"\n🎉 You can now use the converted markdown in your RAG pipeline!")
        
    except ImportError:
        print("❌ Error: doc_to_markdown_converter module not found")
        print("Make sure the doc_to_markdown_converter.py file is in the same directory")
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        # Clean up on error
        if os.path.exists(sample_file):
            os.unlink(sample_file)

def show_usage_patterns():
    """Show common usage patterns for RAG workflows."""
    print("\n" + "=" * 60)
    print("COMMON RAG WORKFLOW USAGE PATTERNS:")
    print("=" * 60)
    
    patterns = [
        {
            "name": "Single Confluence .doc Export",
            "command": "python doc_to_markdown_converter.py confluence_export.doc",
            "description": "Convert a single Confluence .doc export to markdown (most common)"
        },
        {
            "name": "Batch Process Confluence Exports",
            "command": "python doc_to_markdown_converter.py -d exports/ -od markdown/ --pattern '*.doc'",
            "description": "Convert all .doc files from Confluence space export"
        },
        {
            "name": "RAG-Optimized Conversion",
            "command": "python doc_to_markdown_converter.py document.doc --ignore-images --no-metadata",
            "description": "Clean conversion focused on text content for embeddings"
        },
        {
            "name": "Verbose Debugging Mode",
            "command": "python doc_to_markdown_converter.py confluence_export.doc -v",
            "description": "See detailed detection and processing information"
        },
        {
            "name": "Mixed Document Types",
            "command": "python doc_to_markdown_converter.py -d mixed_docs/ -od converted/",
            "description": "Handle .doc, .docx, .html files together with auto-detection"
        }
    ]
    
    for i, pattern in enumerate(patterns, 1):
        print(f"{i}. {pattern['name']}")
        print(f"   Command: {pattern['command']}")
        print(f"   Use case: {pattern['description']}\n")
    
    print("🔍 Pro Tip: Use the -v (verbose) flag to see how the script detects")
    print("   and processes your Confluence .doc files!")

if __name__ == "__main__":
    run_conversion_example()
    show_usage_patterns()
