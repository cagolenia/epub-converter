import ebooklib
from ebooklib import epub

book = epub.read_epub('Kody.epub')
images = list(book.get_items_of_type(ebooklib.ITEM_IMAGE))

print(f'Total images in EPUB: {len(images)}')
print('\nFirst 5 images:')
for img in images[:5]:
    content = img.get_content()
    print(f'{img.get_name()}: {len(content)} bytes')
    # Check if it's a valid JPEG
    if len(content) > 2:
        print(f'  First bytes: {content[:2].hex()}')
