import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

book = epub.read_epub('Kody.epub')

# Get first document with an image
for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
    content = item.get_content().decode('utf-8')
    soup = BeautifulSoup(content, 'html.parser')
    images = soup.find_all('img')
    
    if images:
        print(f"Document: {item.get_name()}")
        print("="*80)
        print(content[:2000])  # Print first 2000 chars
        print("\n" + "="*80)
        break
