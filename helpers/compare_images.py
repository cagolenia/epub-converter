import ebooklib
from ebooklib import epub
import os

book = epub.read_epub('Kody.epub')
images = list(book.get_items_of_type(ebooklib.ITEM_IMAGE))

# Get first image from EPUB
first_image = images[0]
epub_content = first_image.get_content()

# Get the extracted file
extracted_path = os.path.join('temp_html', first_image.get_name())
if os.path.exists(extracted_path):
    with open(extracted_path, 'rb') as f:
        extracted_content = f.read()
    
    print(f'Image name: {first_image.get_name()}')
    print(f'EPUB content size: {len(epub_content)} bytes')
    print(f'Extracted file size: {len(extracted_content)} bytes')
    print(f'Files match: {epub_content == extracted_content}')
    
    # Check file headers
    print(f'\nEPUB first 10 bytes: {epub_content[:10].hex()}')
    print(f'Extracted first 10 bytes: {extracted_content[:10].hex()}')
else:
    print(f'Extracted file not found: {extracted_path}')
