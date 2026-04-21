import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://finance.sina.com.cn/',
}

# 测试不同板块
test_nodes = ['sh_a', 'sz_a', 'gem']

for node in test_nodes:
    url = f'https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=1&num=5&sort=price&asc=0&node={node}&symbol=&_s_r_a=auto'
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = json.loads(resp.text)
        if data:
            print(f'板块{node}: {len(data)}只股票')
            print(f'  示例: {data[0]["code"]} {data[0]["name"]} 价格:{data[0]["trade"]} 市盈率:{data[0]["per"]} 总市值:{data[0]["mktcap"]}')
    except Exception as e:
        print(f'板块{node} Error: {e}')
