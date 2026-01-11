import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

book = epub.read_epub('Kody.epub')

# Check all items in the EPUB
print("All items in EPUB:")
for item in book.get_items():
    item_type = type(item).__name__
    print(f"Type: {item_type}, Name: {item.get_name()}, Size: {len(item.get_content())} bytes")
    
print("\n" + "="*80)
print("Checking HTML content for image references:")
print("="*80 + "\n")

# Check HTML documents for image references
for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
    content = item.get_content().decode('utf-8')
    soup = BeautifulSoup(content, 'html.parser')
    images = soup.find_all('img')
    
    if images:
        print(f"\nDocument: {item.get_name()}")
        for img in images:
            print(f"  <img> src='{img.get('src', 'NO SRC')}' alt='{img.get('alt', 'NO ALT')}'")
