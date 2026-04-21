import requests
import re
import json
import time

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Referer': 'https://q.10jqka.com.cn/'}

# 使用同花顺概念板块排行API
# 885001是概念板块指数
url = 'https://d.10jqka.com.cn/v2/blockrank/885001/8/d10000.js'

try:
    resp = requests.get(url, headers=headers, timeout=10)
    print(f'Status: {resp.status_code}')
    print(f'Response length: {len(resp.text)}')
    print(f'Response: {resp.text[:1000]}')
except Exception as e:
    print(f'Error: {e}')
