import requests
from bs4 import BeautifulSoup
import re
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# 测试新闻API
print('=== 测试新闻API ===')

# 测试不同的API参数
params_list = [
    {'page': 1, 'tag': '', 'track': 'website', 'field': 'time', 'order': 'desc', 'type': '1'},
    {'page': 1, 'tag': '-21101', 'track': 'website', 'field': 'time', 'order': 'desc', 'type': '1'},
    {'page': 1, 'tag': '21101', 'track': 'website', 'field': 'time', 'order': 'desc', 'type': '1'},
]

for params in params_list:
    print('\nParams: %s' % params)
    try:
        r = requests.get('https://news.10jqka.com.cn/tapp/news/push/stock/', 
                         params=params, headers=headers, timeout=10)
        data = r.json()
        items = data.get('data', {}).get('list', [])
        print('Found %d items' % len(items))
        for i, item in enumerate(items[:5]):
            print('  %d: %s' % (i, item.get('title', '')[:80]))
    except Exception as e:
        print('Error: %s' % e)
