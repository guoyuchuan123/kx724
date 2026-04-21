import requests
import json
import time

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Referer': 'https://q.10jqka.com.cn/'}

# 获取同花顺概念板块列表
url = 'https://d.10jqka.com.cn/v2/blockrank/885001/199112/d10000.js'

try:
    resp = requests.get(url, headers=headers, timeout=10)
    text = resp.text[:-1]
    text = text.split('{"block":')[-1]
    text = '{"block":' + text
    text = text.replace('null', 'None')
    data = eval(text)
    items = data.get('items', [])
    print(f'共获取到 {len(items)} 个概念板块')
    
    concepts = {}
    for item in items:
        code = item.get('5', '')
        name = item.get('55', '')
        if code and name:
            concepts[name] = code
    
    # 输出为Python字典格式
    print('\n\n# 概念板块代码映射')
    count = 0
    line = "concept_map = {\n"
    for name, code in sorted(concepts.items()):
        line += f"    '{name}': '{code}',\n"
        count += 1
    
    line += "}\n"
    print(f'共 {count} 个概念')
    print(line[:2000])
    print('...')
    
    # 保存到文件
    with open('d:/kx724/concept_codes.py', 'w', encoding='utf-8') as f:
        f.write(line)
    print(f'\n已保存到 d:/kx724/concept_codes.py')
    
except Exception as e:
    print(f'Error: {e}')
