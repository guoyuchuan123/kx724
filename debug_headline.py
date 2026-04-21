import requests
from bs4 import BeautifulSoup
import re

r = requests.get('https://www.10jqka.com.cn/', headers={'User-Agent': 'Mozilla/5.0'})
r.encoding = 'utf-8'
soup = BeautifulSoup(r.text, 'html.parser')

print('=== Page title ===')
print(soup.title)

print('\n=== All div classes containing "news" or "head" ===')
for div in soup.find_all(['div', 'section']):
    cls = div.get('class', [])
    if cls:
        class_str = ' '.join(cls)
        if 'news' in class_str.lower() or 'head' in class_str.lower() or 'focus' in class_str.lower():
            print(f"Class: {class_str}")
            text = div.get_text(strip=True)[:100]
            if text:
                print(f"  Text: {text}")

print('\n=== First 20 links ===')
links = soup.find_all('a', href=True)
for i, link in enumerate(links[:20]):
    href = link.get('href', '')
    text = link.get_text(strip=True)[:80]
    if text:
        print(f"{i+1}. {text}")
        print(f"   href: {href}")
