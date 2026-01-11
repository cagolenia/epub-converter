import ebooklib
from ebooklib import epub

book = epub.read_epub('Kody.epub')

print("All document items:")
for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
    item_type = type(item).__name__
    item_type_code = item.get_type()
    print(f"Name: {item.get_name()}, Type: {item_type}, Type Code: {item_type_code}")
    
print("\n" + "="*80)
print("Navigation items:")
for item in book.get_items():
    if item.get_type() == ebooklib.ITEM_NAVIGATION:
        print(f"Name: {item.get_name()}, Type: {type(item).__name__}, Type Code: {item.get_type()}")
