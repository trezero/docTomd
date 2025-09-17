# Doc to Markdown Converter for RAG Workflows

A comprehensive Python script that converts various document formats (.doc, .docx, .html, .txt, .rtf) to clean, well-formatted markdown files optimized for RAG (Retrieval-Augmented Generation) workflows.

## Features

- **Multi-format Support**: Handles HTML, MHTML (MIME HTML), DOCX, DOC, RTF, and plain text files
- **Confluence Export Handling**: **Specially designed to handle Confluence .doc exports that contain MHTML content**
- **Smart Content Detection**: Automatically detects file content regardless of extension
- **RAG Optimization**: Produces clean markdown optimized for vector embedding and retrieval
- **Batch Processing**: Convert multiple files at once
- **Metadata Headers**: Adds YAML frontmatter for better document organization
- **Configurable Output**: Customizable formatting options
- **Cross-platform**: Works on Windows, macOS, and Linux

## Important Note About Confluence Exports

**Confluence exports often come with `.doc` extensions even though they contain MHTML (HTML) content, not actual Microsoft Word documents.** This script automatically detects and handles these files correctly:

- ✅ **Auto-Detection**: Recognizes Confluence MHTML content regardless of file extension
- ✅ **Smart Parsing**: Handles `.doc` files that are actually MHTML/HTML exports
- ✅ **Robust Processing**: Multiple encoding support and fallback mechanisms
- ✅ **Content-Based**: Detection based on file content, not just extension

## Installation

### 1. Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### 2. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

Or install manually:
```bash
pip install beautifulsoup4 html2text python-docx markdownify mammoth lxml
```

### 3. Download the Script
Save the `doc_to_markdown_converter.py` file to your desired directory.

## Usage

### Command Line Interface

#### Basic Usage
```bash
# Convert Confluence .doc export (most common use case)
python doc_to_markdown_converter.py confluence_export.doc

# Convert any supported file
python doc_to_markdown_converter.py input.html

# Convert with custom output path
python doc_to_markdown_converter.py input.doc -o output.md

# Convert without metadata headers
python doc_to_markdown_converter.py input.doc --no-metadata
```

#### Batch Conversion
```bash
# Convert all files in a directory
python doc_to_markdown_converter.py -d documents/

# Convert to specific output directory
python doc_to_markdown_converter.py -d documents/ -od markdown_files/

# Convert only .doc files (common for Confluence exports)
python doc_to_markdown_converter.py -d documents/ --pattern "*.doc"
```

#### Advanced Options
```bash
# Verbose logging (helpful for troubleshooting)
python doc_to_markdown_converter.py input.doc -v

# Ignore links and images (good for RAG)
python doc_to_markdown_converter.py input.doc --ignore-links --ignore-images

# Show help
python doc_to_markdown_converter.py --help
```

### Windows Batch Script

For Windows users, use the included `convert_docs.bat` file:

1. Double-click `convert_docs.bat`
2. Choose conversion type (single file or batch)
3. Follow the prompts

### Python API Usage

```python
from doc_to_markdown_converter import DocToMarkdownConverter

# Initialize converter
converter = DocToMarkdownConverter({
    'ignore_images': True,
    'ignore_links': False,
    'body_width': 0
})

# Convert single file (works with .doc Confluence exports)
output_path = converter.convert_file('confluence_export.doc', 'output.md')

# Batch convert
converted_files = converter.batch_convert('documents/', 'markdown_output/')
```

## Supported File Types

| Format | Extension | Description | Notes |
|--------|-----------|-------------|-------|
| **Confluence Exports** | **.doc** | **MHTML content with .doc extension** | **Most common Confluence export format** |
| HTML | .html, .htm | Standard HTML files | Direct HTML conversion |
| MHTML | Any (detected by content) | MIME HTML files | Auto-detected by content |
| DOCX | .docx | Microsoft Word documents (2007+) | Binary Word format |
| DOC | .doc | Legacy Microsoft Word documents | True Word format (rare) |
| RTF | .rtf | Rich Text Format | Cross-platform text format |
| Text | .txt, .md | Plain text and markdown files | Direct processing |

## How Confluence Export Detection Works

The script uses intelligent content detection:

1. **Content Analysis**: Reads file header to identify MHTML markers
2. **Confluence Signatures**: Looks for "Exported From Confluence", MIME boundaries, etc.
3. **Extension Fallback**: If a `.doc` file isn't a real Word document, treats as MHTML
4. **Multiple Encodings**: Tries UTF-8, Latin1, CP1252 to handle various exports
5. **Robust Parsing**: Handles quoted-printable encoding and MIME structure

### Example Detection Log
```
INFO - Detected MHTML content in confluence_export.doc (extension: .doc)
INFO - Detected file type: mhtml
INFO - Extracted 15,234 characters of HTML content from MHTML
```

## Configuration Options

The converter supports various configuration options:

```python
config = {
    'ignore_links': False,      # Keep or remove links
    'ignore_images': True,      # Remove images (recommended for RAG)
    'ignore_emphasis': False,   # Keep bold/italic formatting
    'body_width': 0,           # No line wrapping (recommended for RAG)
}
```

## Output Format

The converter produces clean markdown with:

- **YAML Frontmatter**: Contains metadata like title, source file, and conversion date
- **Normalized Headers**: Proper markdown header formatting
- **Clean Lists**: Consistent list formatting
- **Preserved Structure**: Tables, code blocks, and other structures maintained
- **RAG-Optimized**: No excessive formatting that might confuse embeddings

### Example Output (from Confluence .doc export)

```markdown
---
title: "AI+ 2.0 Release Notes"
source_file: "confluence_export.doc"
converted_date: "2025-09-17T15:33:16"
format: "markdown"
---

# AI+ 2.0 Release Notes

**Release Date:** June 2024

**Bundle Name:** AI+ 2.0 OnPrem Suite

## Purpose

This release introduces AI+ 2.0, a comprehensive suite of onPrem AI features designed for seamless integration with SWARM, OM, and iconik.

## What's New in AI+ 2.0?

- **Advanced Transcription:** Automatically transcribe and generate robust metadata values in multiple languages
- **AutoTranslation:** Translate spoken audio into 20+ languages
- **Facial Recognition:** Identify and tag individuals within your media library
- **Robust Object Detection:** Advanced object recognition capabilities
```

## Handling Confluence .doc Exports

The script is specifically designed to handle Confluence exports that come with `.doc` extensions but contain MHTML/HTML content:

1. **Automatic Detection**: Recognizes MIME format by content headers, not file extension
2. **Content Extraction**: Extracts HTML from MIME containers
3. **Encoding Handling**: Supports multiple text encodings (UTF-8, Latin1, CP1252)
4. **Quoted-Printable Decoding**: Handles `=3D`, `=20`, `=E2=80=99` and other encoded characters
5. **Cleanup**: Removes Confluence-specific styling and artifacts
6. **Structure Preservation**: Maintains document hierarchy and formatting

### Common Confluence Export Patterns

The script recognizes these patterns in `.doc` files:

- `MIME-Version: 1.0`
- `Content-Type: multipart/related`
- `Exported From Confluence`
- `boundary="----=_Part_"`
- Quoted-printable encoding (`=3D`, `=20`, etc.)

## RAG Optimization Features

- **No Line Wrapping**: Preserves natural text flow for better embeddings
- **Consistent Formatting**: Standardized markdown structure
- **Metadata Headers**: YAML frontmatter for document classification
- **Clean Structure**: Removes extraneous formatting that might confuse AI models
- **Image Handling**: Optionally removes images to focus on text content

## Troubleshooting

### Common Issues

1. **File Extension Confusion**
   - **Problem**: "My .doc file won't convert properly"
   - **Solution**: The script auto-detects content. Use `-v` flag to see detection results
   
2. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Encoding Issues**
   - The script tries multiple encodings automatically
   - For problematic files, check the log for encoding errors

4. **Large Confluence Files**
   - For very large exports, consider processing in batches
   - Monitor memory usage during conversion

### Debugging Confluence Exports

Use verbose mode to see what's happening:

```bash
python doc_to_markdown_converter.py confluence_export.doc -v
```

Expected output:
```
INFO - Converting confluence_export.doc to confluence_export.md
INFO - Detected MHTML content in confluence_export.doc (extension: .doc)
INFO - Detected file type: mhtml
INFO - Extracted 15,234 characters of HTML content from MHTML
INFO - Successfully converted confluence_export.doc to confluence_export.md
```

### Logging

The script creates a `doc_converter.log` file with detailed information about the conversion process. Check this file for debugging information.

## Advanced Usage

### Custom Post-Processing

You can extend the converter with custom post-processing:

```python
class CustomConverter(DocToMarkdownConverter):
    def post_process_markdown(self, markdown: str) -> str:
        # Call parent method
        markdown = super().post_process_markdown(markdown)
        
        # Add custom processing
        # ... your custom logic here ...
        
        return markdown
```

### Integration with RAG Pipelines

The output is optimized for use with popular RAG frameworks:

```python
# Example with LangChain
from langchain.document_loaders import TextLoader
from langchain.text_splitter import MarkdownHeaderTextSplitter

# Load converted markdown
loader = TextLoader('converted_document.md')
documents = loader.load()

# Split by headers for better chunking
splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
)
split_docs = splitter.split_text(documents[0].page_content)
```

## Testing

Run the test script to verify installation:

```bash
python test_converter.py
```

This will:
1. Create a sample Confluence export file
2. Convert it to markdown
3. Display the results
4. Clean up test files

## Common Confluence Export Scenarios

### Scenario 1: Single Document Export
```bash
# Export from Confluence comes as "meeting_notes.doc"
python doc_to_markdown_converter.py meeting_notes.doc
# Creates: meeting_notes.md
```

### Scenario 2: Bulk Documentation Export
```bash
# Multiple .doc files from Confluence space export
python doc_to_markdown_converter.py -d confluence_exports/ -od docs_markdown/
```

### Scenario 3: Mixed File Types
```bash
# Directory with .doc, .docx, and .html files
python doc_to_markdown_converter.py -d mixed_docs/ -od converted/
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This script is provided as-is for educational and commercial use. Feel free to modify and distribute.

## Support

For issues and questions:

1. Check the log file (`doc_converter.log`) for error details
2. Use verbose mode (`-v`) to see detailed processing information
3. Verify all dependencies are installed correctly
4. Test with the provided test script
5. Check file permissions and paths

## Version History

- **v1.0.0**: Initial release with basic conversion support
- **v1.1.0**: Added Confluence MHTML support
- **v1.2.0**: Enhanced RAG optimization features
- **v1.3.0**: Added batch processing and Windows batch script
- **v1.4.0**: **Improved .doc file detection and Confluence export handling**

---

*Last updated: September 17, 2025*

**Ready for your Confluence .doc exports!** 🎉
