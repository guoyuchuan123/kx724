import pandas as pd

user_stocks = [
    '成都路桥', '云南锗业', '南大光电', '安靠智电', '海南矿业', '光华科技', 'ST联创',
    '中船特气', '永和股份', '新亚制程', '中巨芯-U', '石大胜华', '泰和科技', '康鹏科技',
    '三美股份', '金石资源', '闰土股份', '华谊集团', '华盛锂电', '鲁西化工', '泰禾股份',
    '中欣氟材', '立中集团', '永太科技', '大洋生物', '巍华新材', '雅克科技', '多氟多',
    '杉杉股份', '宏源药业', '湖北宜化', '深圳新星', '富祥药业', '包钢股份', '天赐材料',
    '和远气体', '氯碱化工', '联化科技', '巨化股份', '昊华科技', '滨化股份', '八亿时空',
    '尚纬股份', '新宙邦', '云天化', '东阳光', '司太立', '中密控股', '新洋丰', '天域生物',
    '华邦健康', '兴发集团', '天际股份', '华特气体', '东江环保', '华神科技', '新 和 成',
    '孚日股份', '金凯生科'
]

df = pd.read_excel('news_data/化工_2026-04-19.xlsx', sheet_name='化工')
excel_names = set(df['名称'].tolist())
user_names = set(user_stocks)

missing_in_excel = user_names - excel_names
extra_in_excel = excel_names - user_names

print(f'用户提供的股票数量: {len(user_stocks)}')
print(f'Excel中的股票数量: {len(excel_names)}')

if missing_in_excel:
    print(f'\nExcel中缺失的股票 ({len(missing_in_excel)}):')
    for name in sorted(missing_in_excel):
        print(f'  {name}')

if extra_in_excel:
    print(f'\nExcel中多出的股票 ({len(extra_in_excel)}):')
    for name in sorted(extra_in_excel):
        print(f'  {name}')

if not missing_in_excel and not extra_in_excel:
    print('\n完全匹配！')
