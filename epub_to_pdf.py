#!/usr/bin/env python3
"""
EPUB to PDF Converter
A command-line tool to convert EPUB files to PDF format.

Author: cagoleniawrite
Version: 1.0
Date: 2026-01-05
"""

import argparse
import os
import sys
import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import Optional, List, Tuple
import xml.etree.ElementTree as ET

try:
    import ebooklib
    from ebooklib import epub
except ImportError:
    print("Error: ebooklib is not installed. Install it with: pip install ebooklib")
    sys.exit(1)

try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
except ImportError:
    print("Error: weasyprint is not installed. Install it with: pip install weasyprint")
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: beautifulsoup4 is not installed. Install it with: pip install beautifulsoup4")
    sys.exit(1)


class EPUBConverter:
    """Main converter class for EPUB to PDF conversion."""
    
    def __init__(self, verbose: bool = False, preserve_temp: bool = False):
        self.verbose = verbose
        self.preserve_temp = preserve_temp
        self.temp_dir = None
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages if verbose mode is enabled."""
        if self.verbose:
            print(f"[{level}] {message}")
    
    def validate_epub(self, epub_path: str) -> bool:
        """
        Validate that the input file is a valid EPUB.
        
        Args:
            epub_path: Path to the EPUB file
            
        Returns:
            True if valid, False otherwise
        """
        self.log(f"Validating EPUB file: {epub_path}")
        
        # Check file exists
        if not os.path.exists(epub_path):
            print(f"Error: File not found: {epub_path}", file=sys.stderr)
            return False
        
        # Check file extension
        if not epub_path.lower().endswith('.epub'):
            print(f"Error: File does not have .epub extension: {epub_path}", file=sys.stderr)
            return False
        
        # Check if it's a valid zip file
        if not zipfile.is_zipfile(epub_path):
            print(f"Error: File is not a valid EPUB (not a zip archive): {epub_path}", file=sys.stderr)
            return False
        
        # Try to open with ebooklib
        try:
            book = epub.read_epub(epub_path)
            self.log("EPUB validation successful")
            return True
        except Exception as e:
            print(f"Error: Failed to read EPUB file: {e}", file=sys.stderr)
            return False
    
    def extract_metadata(self, book: epub.EpubBook) -> dict:
        """
        Extract metadata from EPUB.
        
        Args:
            book: EpubBook object
            
        Returns:
            Dictionary containing metadata
        """
        self.log("Extracting metadata")
        
        metadata = {
            'title': book.get_metadata('DC', 'title'),
            'author': book.get_metadata('DC', 'creator'),
            'publisher': book.get_metadata('DC', 'publisher'),
            'language': book.get_metadata('DC', 'language'),
            'date': book.get_metadata('DC', 'date'),
            'identifier': book.get_metadata('DC', 'identifier'),
        }
        
        # Extract first value if multiple
        for key in metadata:
            if metadata[key] and isinstance(metadata[key], list) and len(metadata[key]) > 0:
                metadata[key] = metadata[key][0][0] if isinstance(metadata[key][0], tuple) else metadata[key][0]
            elif not metadata[key]:
                metadata[key] = None
        
        self.log(f"Title: {metadata.get('title', 'Unknown')}")
        self.log(f"Author: {metadata.get('author', 'Unknown')}")
        
        return metadata
    
    def get_page_size(self, page_size: str) -> Tuple[str, str]:
        """
        Get page dimensions for the given page size.
        
        Args:
            page_size: Page size name (A4, Letter, Custom)
            
        Returns:
            Tuple of (width, height) in CSS format
        """
        sizes = {
            'A4': ('210mm', '297mm'),
            'LETTER': ('8.5in', '11in'),
            'A5': ('148mm', '210mm'),
            'LEGAL': ('8.5in', '14in'),
        }
        
        return sizes.get(page_size.upper(), sizes['A4'])
    
    def create_css(self, page_size: str = 'A4', margins: int = 20, font_size: int = 12) -> str:
        """
        Create CSS styling for the PDF.
        
        Args:
            page_size: Page size (A4, Letter, etc.)
            margins: Margin size in mm
            font_size: Base font size in pt
            
        Returns:
            CSS string
        """
        width, height = self.get_page_size(page_size)
        
        css = f"""
        @page {{
            size: {width} {height};
            margin: {margins}mm;
            
            @top-center {{
                content: string(book-title);
                font-size: 9pt;
                color: #666;
            }}
            
            @bottom-center {{
                content: counter(page);
                font-size: 9pt;
                color: #666;
            }}
        }}
        
        body {{
            font-family: Georgia, 'Times New Roman', serif;
            font-size: {font_size}pt;
            line-height: 1.6;
            text-align: justify;
            color: #000;
        }}
        
        h1 {{
            string-set: book-title content();
            font-size: {font_size * 2}pt;
            font-weight: bold;
            margin-top: 1em;
            margin-bottom: 0.5em;
            page-break-before: always;
            page-break-after: avoid;
        }}
        
        h2 {{
            font-size: {font_size * 1.5}pt;
            font-weight: bold;
            margin-top: 0.8em;
            margin-bottom: 0.4em;
            page-break-after: avoid;
        }}
        
        h3 {{
            font-size: {font_size * 1.25}pt;
            font-weight: bold;
            margin-top: 0.6em;
            margin-bottom: 0.3em;
            page-break-after: avoid;
        }}
        
        h4, h5, h6 {{
            font-size: {font_size * 1.1}pt;
            font-weight: bold;
            margin-top: 0.5em;
            margin-bottom: 0.25em;
            page-break-after: avoid;
        }}
        
        p {{
            margin: 0.5em 0;
            text-indent: 1.5em;
            orphans: 3;
            widows: 3;
        }}
        
        p:first-child,
        h1 + p, h2 + p, h3 + p, h4 + p {{
            text-indent: 0;
        }}
        
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1em auto;
            page-break-inside: avoid;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1em 0;
            page-break-inside: avoid;
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        
        blockquote {{
            margin: 1em 2em;
            padding: 0.5em 1em;
            border-left: 3px solid #ccc;
            font-style: italic;
        }}
        
        ul, ol {{
            margin: 0.5em 0;
            padding-left: 2em;
        }}
        
        li {{
            margin: 0.25em 0;
        }}
        
        pre, code {{
            font-family: 'Courier New', monospace;
            background-color: #f5f5f5;
            padding: 0.2em 0.4em;
            border-radius: 3px;
        }}
        
        pre {{
            padding: 1em;
            overflow-x: auto;
            page-break-inside: avoid;
        }}
        
        a {{
            color: #0066cc;
            text-decoration: none;
        }}
        
        hr {{
            border: none;
            border-top: 1px solid #ccc;
            margin: 2em 0;
        }}
        
        .chapter {{
            page-break-before: always;
        }}
        
        /* Table of Contents styling */
        .toc-page {{
            page-break-after: always;
        }}
        
        .toc-title {{
            font-size: {font_size * 1.8}pt;
            font-weight: bold;
            text-align: center;
            margin-bottom: 1em;
            text-indent: 0;
        }}
        
        .toc-list {{
            list-style: none;
            padding-left: 0;
        }}
        
        .toc-list li {{
            margin: 0.5em 0;
            text-indent: 0;
        }}
        
        .toc-level-1 {{
            font-weight: bold;
            margin-top: 0.8em;
        }}
        
        .toc-level-2 {{
            padding-left: 1.5em;
        }}
        
        .toc-level-3 {{
            padding-left: 3em;
            font-size: 0.95em;
        }}
        
        .toc-list a {{
            color: #000;
            text-decoration: none;
            display: block;
        }}
        
        .toc-list a:hover {{
            color: #0066cc;
        }}        """
        
        return css
    
    def extract_toc(self, book: epub.EpubBook) -> List[Tuple[str, str, int]]:
        """
        Extract table of contents from EPUB.
        
        Args:
            book: EpubBook object
            
        Returns:
            List of tuples (title, href, level)
        """
        toc_entries = []
        
        def process_toc_item(item, level=1):
            if isinstance(item, tuple):
                # Item is (Section, list_of_children)
                section, children = item
                if hasattr(section, 'title') and hasattr(section, 'href'):
                    toc_entries.append((section.title, section.href, level))
                for child in children:
                    process_toc_item(child, level + 1)
            elif isinstance(item, epub.Link):
                # Item is a Link object
                toc_entries.append((item.title, item.href, level))
            elif hasattr(item, 'title') and hasattr(item, 'href'):
                # Item has title and href attributes
                toc_entries.append((item.title, item.href, level))
        
        # Process the table of contents
        toc = book.toc
        if toc:
            for item in toc:
                process_toc_item(item)
        
        self.log(f"Extracted {len(toc_entries)} TOC entries")
        return toc_entries
    
    def process_html_content(self, html_content: str, base_path: str = "") -> str:
        """
        Process and clean HTML content.
        
        Args:
            html_content: Raw HTML content
            base_path: Base path for resolving relative URLs (unused but kept for compatibility)
            
        Returns:
            Processed HTML string
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style tags
        for tag in soup.find_all(['script', 'style']):
            tag.decompose()
        
        # Fix image paths - keep them relative to the HTML file location
        # Images are extracted preserving their directory structure, so we just
        # need to ensure the paths are clean and use forward slashes
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src and not src.startswith(('http://', 'https://', 'data:')):
                # Clean up the path - remove leading slashes and '../' patterns
                # but keep the relative path structure (e.g., "images/foo.jpg")
                clean_src = src.lstrip('./').lstrip('/')
                # Normalize to forward slashes for web compatibility
                img['src'] = clean_src.replace('\\', '/')
        
        return str(soup)
    
    def convert(
        self,
        epub_path: str,
        output_path: Optional[str] = None,
        page_size: str = 'A4',
        margins: int = 20,
        font_size: int = 12,
        include_toc: bool = True,
        preserve_temp: bool = None
    ) -> bool:
        """
        Convert EPUB to PDF.
        
        Args:
            epub_path: Path to input EPUB file
            output_path: Path to output PDF file (optional)
            page_size: Page size (A4, Letter, etc.)
            margins: Margin size in mm
            font_size: Base font size in pt
            include_toc: Include table of contents
            preserve_temp: Preserve temporary HTML files in temp_html folder
            
        Returns:
            True if successful, False otherwise
        """
        # Validate input
        if not self.validate_epub(epub_path):
            return False
        
        # Determine output path
        if not output_path:
            epub_file = Path(epub_path)
            output_path = str(epub_file.with_suffix('.pdf'))
        
        self.log(f"Output will be saved to: {output_path}")
        
        try:
            # Read EPUB
            self.log("Reading EPUB file...")
            book = epub.read_epub(epub_path)
            
            # Extract metadata
            metadata = self.extract_metadata(book)
            
            # Extract table of contents if requested
            toc_entries = []
            if include_toc:
                toc_entries = self.extract_toc(book)
            
            # Determine if we should preserve temp files
            if preserve_temp is None:
                preserve_temp = self.preserve_temp
            
            # Create temporary directory for extraction
            if preserve_temp:
                # Create temp_html directory next to output file
                output_dir = os.path.dirname(os.path.abspath(output_path))
                self.temp_dir = os.path.join(output_dir, 'temp_html')
                os.makedirs(self.temp_dir, exist_ok=True)
                self.log(f"Created temp_html directory: {self.temp_dir}")
            else:
                self.temp_dir = tempfile.mkdtemp()
                self.log(f"Created temporary directory: {self.temp_dir}")
            
            # Extract images first and build image map
            self.log("Extracting images...")
            image_map = {}
            image_count = 0
            
            # Extract regular images
            for item in book.get_items_of_type(ebooklib.ITEM_IMAGE):
                img_name = item.get_name()
                img_path = os.path.join(self.temp_dir, img_name)
                os.makedirs(os.path.dirname(img_path), exist_ok=True)
                with open(img_path, 'wb') as img_file:
                    img_file.write(item.get_content())
                # Store mapping of original path to extracted path
                image_map[img_name] = img_path
                # Also store without leading path components for flexibility
                image_map[img_name.lstrip('./')] = img_path
                image_count += 1
            
            # Also extract cover images (they have a different type)
            for item in book.get_items_of_type(ebooklib.ITEM_COVER):
                img_name = item.get_name()
                img_path = os.path.join(self.temp_dir, img_name)
                os.makedirs(os.path.dirname(img_path), exist_ok=True)
                with open(img_path, 'wb') as img_file:
                    img_file.write(item.get_content())
                image_map[img_name] = img_path
                image_map[img_name.lstrip('./')] = img_path
                image_count += 1
            
            self.log(f"Extracted {image_count} images")
            
            # Build HTML content
            self.log("Building HTML content...")
            html_parts = ['<!DOCTYPE html><html><head><meta charset="utf-8">']
            html_parts.append(f'<title>{metadata.get("title", "Converted Book")}</title>')
            html_parts.append('</head><body>')
            
            # Add title page
            if metadata.get('title'):
                html_parts.append('<div class="title-page" style="text-align: center; padding: 5em 2em;">')
                html_parts.append(f'<h1 style="font-size: 24pt; margin-bottom: 1em;">{metadata["title"]}</h1>')
                if metadata.get('author'):
                    html_parts.append(f'<p style="font-size: 14pt;">by {metadata["author"]}</p>')
                if metadata.get('publisher'):
                    html_parts.append(f'<p style="font-size: 12pt; margin-top: 2em;">{metadata["publisher"]}</p>')
                html_parts.append('</div>')
                html_parts.append('<div style="page-break-after: always;"></div>')
            
            # Add table of contents if requested and entries exist
            if include_toc and toc_entries:
                html_parts.append('<div class="toc-page">')
                html_parts.append('<h2 class="toc-title">Table of Contents</h2>')
                html_parts.append('<ul class="toc-list">')
                for title, href, level in toc_entries:
                    # Clean href to create an anchor ID
                    anchor_id = href.replace('/', '_').replace('.', '_').replace('#', '_').replace('.xhtml', '').replace('.html', '')
                    # Escape HTML entities in title
                    from html import escape
                    safe_title = escape(title)
                    html_parts.append(f'<li class="toc-level-{level}"><a href="#{anchor_id}">{safe_title}</a></li>')
                html_parts.append('</ul>')
                html_parts.append('</div>')
            
            # Create mapping of file names to anchor IDs for linking
            anchor_map = {}
            if include_toc and toc_entries:
                for title, href, level in toc_entries:
                    # Extract filename from href (before any # anchor)
                    filename = href.split('#')[0]
                    anchor_id = href.replace('/', '_').replace('.', '_').replace('#', '_').replace('.xhtml', '').replace('.html', '')
                    anchor_map[filename] = anchor_id
            
            # Process documents in reading order, but skip navigation/TOC documents
            all_items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
            # Filter out navigation items (toc.xhtml, nav.xhtml, etc.) to avoid duplicate TOCs
            # Check both the type and the class name since EpubNav items still have ITEM_DOCUMENT type
            items = [item for item in all_items if type(item).__name__ != 'EpubNav']
            total_items = len(items)
            
            for idx, item in enumerate(items, 1):
                if self.verbose:
                    progress = (idx / total_items) * 100
                    print(f"\rProcessing content: {progress:.1f}%", end='', flush=True)
                
                try:
                    content = item.get_content().decode('utf-8')
                    processed_content = self.process_html_content(content, self.temp_dir)
                    
                    # Extract body content
                    soup = BeautifulSoup(processed_content, 'html.parser')
                    body = soup.find('body')
                    
                    if body:
                        # Add anchor ID to first heading if this file is in the TOC
                        item_name = item.get_name()
                        if include_toc and item_name in anchor_map:
                            first_heading = body.find(['h1', 'h2', 'h3'])
                            if first_heading:
                                # Add anchor ID for TOC linking
                                first_heading['id'] = anchor_map[item_name]
                                # Add chapter class
                                first_heading['class'] = first_heading.get('class', []) + ['chapter']
                        else:
                            # Just add chapter class to first heading if exists
                            first_heading = body.find(['h1', 'h2', 'h3'])
                            if first_heading and 'class' not in first_heading.attrs:
                                first_heading['class'] = first_heading.get('class', []) + ['chapter']
                        
                        html_parts.append(str(body))
                    else:
                        html_parts.append(processed_content)
                        
                except Exception as e:
                    self.log(f"Warning: Failed to process item {item.get_name()}: {e}", "WARN")
            
            if self.verbose:
                print()  # New line after progress
            
            html_parts.append('</body></html>')
            html_content = '\n'.join(html_parts)
            
            # Save HTML to temp file
            html_file_path = os.path.join(self.temp_dir, 'book.html')
            with open(html_file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Generate CSS
            self.log("Generating CSS...")
            css_content = self.create_css(page_size, margins, font_size)
            
            # Convert to PDF
            self.log("Converting to PDF...")
            font_config = FontConfiguration()
            
            html_obj = HTML(filename=html_file_path, base_url=self.temp_dir)
            css_obj = CSS(string=css_content, font_config=font_config)
            
            html_obj.write_pdf(
                output_path,
                stylesheets=[css_obj],
                font_config=font_config
            )
            
            self.log(f"PDF generated successfully: {output_path}")
            print(f"✓ Conversion successful: {output_path}")
            
            # Show temp_html location if preserved
            if preserve_temp:
                print(f"📁 Temporary HTML files preserved in: {self.temp_dir}")
            
            return True
            
        except Exception as e:
            print(f"Error during conversion: {e}", file=sys.stderr)
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False
            
        finally:
            # Clean up temp directory (unless preserve_temp is enabled)
            if preserve_temp is None:
                preserve_temp = self.preserve_temp
            
            if not preserve_temp and self.temp_dir and os.path.exists(self.temp_dir):
                try:
                    shutil.rmtree(self.temp_dir)
                    self.log("Cleaned up temporary files")
                except Exception as e:
                    self.log(f"Warning: Failed to clean up temp directory: {e}", "WARN")
    
    def batch_convert(
        self,
        epub_files: List[str],
        output_dir: Optional[str] = None,
        **kwargs
    ) -> Tuple[int, int]:
        """
        Convert multiple EPUB files to PDF.
        
        Args:
            epub_files: List of EPUB file paths
            output_dir: Output directory for PDF files
            **kwargs: Additional arguments for convert()
            
        Returns:
            Tuple of (successful_count, failed_count)
        """
        successful = 0
        failed = 0
        
        total = len(epub_files)
        print(f"Starting batch conversion of {total} files...")
        
        for idx, epub_path in enumerate(epub_files, 1):
            print(f"\n[{idx}/{total}] Converting: {os.path.basename(epub_path)}")
            
            # Determine output path
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(
                    output_dir,
                    Path(epub_path).stem + '.pdf'
                )
            else:
                output_path = None
            
            # Convert
            if self.convert(epub_path, output_path, **kwargs):
                successful += 1
            else:
                failed += 1
        
        print(f"\n{'='*60}")
        print(f"Batch conversion complete:")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"{'='*60}")
        
        return successful, failed


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Convert EPUB files to PDF format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic conversion
  %(prog)s book.epub

  # Specify output file
  %(prog)s book.epub -o output.pdf

  # Custom page size and margins
  %(prog)s book.epub --page-size A4 --margins 25

  # Batch conversion
  %(prog)s *.epub --output-dir ./pdfs

  # Verbose mode for debugging
  %(prog)s book.epub -v
        """
    )
    
    parser.add_argument(
        'epub_files',
        nargs='+',
        help='EPUB file(s) to convert'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output PDF file path (for single file conversion)'
    )
    
    parser.add_argument(
        '--output-dir',
        help='Output directory for batch conversion'
    )
    
    parser.add_argument(
        '--page-size',
        default='A4',
        choices=['A4', 'Letter', 'A5', 'Legal'],
        help='Page size for PDF (default: A4)'
    )
    
    parser.add_argument(
        '--margins',
        type=int,
        default=20,
        help='Page margins in millimeters (default: 20)'
    )
    
    parser.add_argument(
        '--font-size',
        type=int,
        default=12,
        help='Base font size in points (default: 12)'
    )
    
    parser.add_argument(
        '--no-toc',
        action='store_true',
        help='Disable table of contents generation'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--preserve-temp',
        action='store_true',
        help='Preserve temporary HTML files in temp_html folder for debugging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0'
    )
    
    args = parser.parse_args()
    
    # Create converter
    converter = EPUBConverter(verbose=args.verbose, preserve_temp=args.preserve_temp)
    
    # Check if batch conversion
    if len(args.epub_files) > 1 or args.output_dir:
        # Batch mode
        converter.batch_convert(
            args.epub_files,
            output_dir=args.output_dir,
            page_size=args.page_size,
            margins=args.margins,
            font_size=args.font_size,
            include_toc=not args.no_toc
        )
    else:
        # Single file mode
        success = converter.convert(
            args.epub_files[0],
            output_path=args.output,
            page_size=args.page_size,
            margins=args.margins,
            font_size=args.font_size,
            include_toc=not args.no_toc
        )
        
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
