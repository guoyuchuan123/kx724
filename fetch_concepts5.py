import requests
import re
import json
import time

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Referer': 'https://q.10jqka.com.cn/'}

# 获取概念板块列表页面
url = 'https://q.10jqka.com.cn/gn/'
resp = requests.get(url, headers=headers, timeout=10)

# 从页面中提取概念代码
# 格式通常是 code/30xxxx/ 其中30xxxx是概念ID
pattern = r'gn/detail/code/(\d+)/'
code_ids = re.findall(pattern, resp.text)

print(f'找到 {len(code_ids)} 个概念ID')
print(f'示例: {code_ids[:10]}')

# 获取概念名称和对应的885代码
concepts = {}
for i, code_id in enumerate(code_ids):
    url = f'https://d.10jqka.com.cn/v2/blockrank/{code_id}/199112/d10000.js'
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        text = resp.text[:-1]
        text = text.split('{"block":')[-1]
        text = '{"block":' + text
        text = text.replace('null', 'None')
        data = eval(text)
        block_info = data.get('block', {})
        name = block_info.get('blockname', block_info.get('name', ''))
        # 从blockinfo中获取885代码
        block_code = block_info.get('code', '')
        if name and block_code:
            concepts[name] = block_code
            print(f'{i+1}. {name}: {block_code}')
    except Exception as e:
        print(f'Error for {code_id}: {e}')
    
    if i % 10 == 0 and i > 0:
        time.sleep(0.5)

print(f'\n共获取到 {len(concepts)} 个概念板块')

# 保存到文件
with open('d:/kx724/concept_codes.py', 'w', encoding='utf-8') as f:
    f.write('# 同花顺概念板块代码映射\n')
    f.write('concept_map = {\n')
    for name, code in sorted(concepts.items()):
        f.write(f"    '{name}': '{code}',\n")
    f.write('}\n')

print(f'已保存到 d:/kx724/concept_codes.py')
