import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://q.10jqka.com.cn/',
}

# 测试获取全部数据
url = 'https://d.10jqka.com.cn/v2/blockrank/884153/17/d10000.js'

try:
    resp = requests.get(url, headers=headers, timeout=30)
    text = resp.text[:-1]
    text = text.split('{"block":')[-1]
    text = '{"block":' + text
    text = text.replace('null', 'None')
    data = eval(text)
    items = data.get('items', [])
    print(f'板块884153: {len(items)}只股票')
    if items:
        print(f'字段: {list(items[0].keys())}')
        # 查找600519
        for item in items:
            if item.get('5') == '600519':
                print(f'\n600519 数据:')
                for k, v in item.items():
                    print(f'  字段{k}: {v}')
                break
except Exception as e:
    print(f'Error: {e}')
