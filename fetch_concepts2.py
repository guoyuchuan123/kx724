import requests
import json
import time

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Referer': 'https://q.10jqka.com.cn/'}

# 尝试获取概念板块列表 - 使用不同的API
urls = [
    'https://d.10jqka.com.cn/v2/blockrank/885/199112/d10000.js',
    'https://d.10jqka.com.cn/v2/blockrank/885001/8/d10000.js',
    'https://q.10jqka.com.cn/gn/',
]

for url in urls:
    print(f'\nTrying: {url}')
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f'Status: {resp.status_code}, Length: {len(resp.text)}')
        print(resp.text[:500])
    except Exception as e:
        print(f'Error: {e}')
