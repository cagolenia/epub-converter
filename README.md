# EPUB to PDF Converter

A powerful command-line tool to convert EPUB e-books to PDF format with high fidelity preservation of formatting, images, and document structure.

## Features

✨ **Core Features:**
- Convert EPUB 2.0 and 3.0 files to PDF
- Preserve text formatting (bold, italic, headings, etc.)
- Maintain chapter structure and navigation
- Embed images in correct positions
- Support for tables, lists, and special formatting
- Extract and include metadata (title, author, publisher)
- Batch conversion of multiple files

⚙️ **Customization Options:**
- Multiple page sizes (A4, Letter, A5, Legal)
- Adjustable margins
- Configurable font size
- Professional PDF styling with page numbers

🚀 **User-Friendly:**
- Simple command-line interface
- Progress indicators
- Verbose mode for debugging
- Clear error messages
- Comprehensive help documentation

## Requirements

- Python 3.8 or higher
- Windows, macOS, or Linux

## Installation

### 1. Clone or Download the Repository

```bash
cd "epub converter"
```

### 2. Install Dependencies

**Standard Installation:**
```bash
pip install -r requirements.txt
```

**Alternative: Install Manually:**
```bash
pip install ebooklib weasyprint beautifulsoup4 lxml Pillow
```

### 3. Verify Installation

```bash
python epub_to_pdf.py --help
```

## Usage

### Basic Conversion

Convert a single EPUB file to PDF:

```bash
python epub_to_pdf.py book.epub
```

This creates `book.pdf` in the same directory.

### Specify Output File

```bash
python epub_to_pdf.py book.epub -o output.pdf
```

or with full path:

```bash
python epub_to_pdf.py book.epub -o "C:\Users\YourName\Documents\mybook.pdf"
```

### Custom Page Size and Margins

```bash
# A4 with 25mm margins
python epub_to_pdf.py book.epub --page-size A4 --margins 25

# Letter size with 20mm margins
python epub_to_pdf.py book.epub --page-size Letter --margins 20

# A5 size (smaller format)
python epub_to_pdf.py book.epub --page-size A5
```

### Adjust Font Size

```bash
# Larger font (14pt)
python epub_to_pdf.py book.epub --font-size 14

# Smaller font (10pt)
python epub_to_pdf.py book.epub --font-size 10
```

### Batch Conversion

Convert multiple EPUB files:

```bash
# Convert all EPUB files in current directory
python epub_to_pdf.py *.epub

# Save to specific output directory
python epub_to_pdf.py *.epub --output-dir ./pdfs

# With custom settings
python epub_to_pdf.py *.epub --output-dir ./pdfs --page-size A4 --font-size 12
```

### Verbose Mode

Enable detailed logging for troubleshooting:

```bash
python epub_to_pdf.py book.epub -v
```

### Combined Options

```bash
python epub_to_pdf.py book.epub -o output.pdf --page-size Letter --margins 25 --font-size 13 -v
```

## Command-Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `epub_files` | - | EPUB file(s) to convert (required) | - |
| `--output` | `-o` | Output PDF file path | Same as input with .pdf |
| `--output-dir` | - | Output directory (batch mode) | Current directory |
| `--page-size` | - | Page size: A4, Letter, A5, Legal | A4 |
| `--margins` | - | Page margins in millimeters | 20 |
| `--font-size` | - | Base font size in points | 12 |
| `--no-toc` | - | Disable table of contents | Enabled |
| `--verbose` | `-v` | Enable verbose output | Disabled |
| `--help` | `-h` | Show help message | - |
| `--version` | - | Show version | - |

## Examples

### Example 1: Basic Conversion

```bash
python epub_to_pdf.py "The Great Gatsby.epub"
```

**Output:** Creates `The Great Gatsby.pdf`

### Example 2: Custom Output Location

```bash
python epub_to_pdf.py "novel.epub" -o "C:\Books\PDF\novel.pdf"
```

### Example 3: Print-Ready Format

```bash
python epub_to_pdf.py book.epub --page-size Letter --margins 30 --font-size 11
```

### Example 4: Large Print Format

```bash
python epub_to_pdf.py book.epub --font-size 16 --margins 25
```

### Example 5: Batch Convert Library

```bash
# Convert entire library
python epub_to_pdf.py "C:\MyBooks\*.epub" --output-dir "C:\MyBooks\PDF" -v
```

### Example 6: Specific Files

```bash
python epub_to_pdf.py book1.epub book2.epub book3.epub --output-dir ./converted
```

## Output Features

The generated PDFs include:

- **Title Page:** Book title, author, and publisher
- **Page Numbers:** Centered at bottom of each page
- **Headers:** Book title at top of pages
- **Professional Typography:**
  - Justified text with proper hyphenation
  - Smart text indentation
  - Widow/orphan control
  - Page break management
- **Formatted Elements:**
  - Headings with appropriate hierarchy
  - Tables with borders
  - Block quotes with left border
  - Code blocks with monospace font
  - Lists (ordered and unordered)
  - Embedded images

## Troubleshooting

### Common Issues

**1. Import Error: Module not found**

```
Error: ebooklib is not installed. Install it with: pip install ebooklib
```

**Solution:** Install the required package:
```bash
pip install ebooklib
```

**2. GTK+ Library Error (WeasyPrint on Windows)**

WeasyPrint requires GTK+ libraries on Windows. Download and install from:
https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases

**3. File Not Found**

```
Error: File not found: book.epub
```

**Solution:** Check the file path and ensure the file exists. Use absolute paths or navigate to the correct directory.

**4. Invalid EPUB**

```
Error: File is not a valid EPUB
```

**Solution:** Verify the EPUB file is not corrupted. Try opening it in an EPUB reader first.

**5. Permission Denied**

```
Error: Permission denied
```

**Solution:** Ensure you have write permissions for the output directory.

**6. Large File Processing**

For very large EPUB files (>50MB), the conversion may take several minutes. Use verbose mode (`-v`) to monitor progress.

### Getting Help

Run with verbose mode to see detailed processing information:

```bash
python epub_to_pdf.py book.epub -v
```

## Limitations

- **DRM Protection:** Cannot convert DRM-protected EPUB files
- **Interactive Content:** EPUB 3.0 multimedia features (audio, video) are excluded
- **Complex CSS:** Some advanced CSS layouts may not render identically
- **Fonts:** Embedded fonts are supported, but may fall back to system fonts
- **File Size:** Very large files (>100MB) may require significant processing time

## Technical Details

### Architecture

```
Input EPUB File
    ↓
Validation & Extraction
    ↓
Metadata Parsing
    ↓
Content Processing (HTML/XHTML)
    ↓
Image Extraction
    ↓
CSS Styling Application
    ↓
PDF Generation (WeasyPrint)
    ↓
Output PDF File
```

### Dependencies

- **ebooklib:** EPUB parsing and manipulation
- **WeasyPrint:** HTML to PDF rendering engine
- **BeautifulSoup4:** HTML parsing and cleaning
- **lxml:** XML processing
- **Pillow:** Image handling

### Supported EPUB Versions

- EPUB 2.0.1
- EPUB 3.0
- EPUB 3.1
- EPUB 3.2
- EPUB 3.3

## Performance

Typical conversion times (tested on modern desktop):

| File Size | Pages | Time |
|-----------|-------|------|
| 1 MB | ~50 | 5-10 seconds |
| 5 MB | ~200 | 15-30 seconds |
| 10 MB | ~400 | 30-60 seconds |
| 50 MB | ~1000 | 2-5 minutes |

## Development

### Project Structure

```
epub converter/
├── epub_to_pdf.py      # Main converter script
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── setup.py           # Installation setup
├── .gitignore         # Git ignore rules
├── prd.md             # Product requirements
└── context.md         # Project context
```

### Testing

To test the converter:

1. Obtain sample EPUB files (use Project Gutenberg for free books)
2. Test basic conversion:
   ```bash
   python epub_to_pdf.py sample.epub -v
   ```
3. Test batch conversion:
   ```bash
   python epub_to_pdf.py *.epub --output-dir test_output
   ```
4. Verify PDF output in a PDF reader

### Contributing

Contributions are welcome! Areas for improvement:

- Enhanced CSS support
- Better font handling
- Table of contents generation with bookmarks
- Progress bar for large files
- GUI interface
- Additional page size options
- Custom styling templates

## License

This project is provided as-is for educational and personal use.

## Credits

**Author:** cagoleniawrite  
**Version:** 1.0  
**Date:** January 2026

Built with:
- [ebooklib](https://github.com/aerkalov/ebooklib) - EPUB parsing
- [WeasyPrint](https://weasyprint.org/) - PDF generation
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML processing

## Support

For issues, questions, or feature requests, please check the troubleshooting section above or review the PRD document for detailed requirements.

---

**Happy Converting! 📚 → 📄**
