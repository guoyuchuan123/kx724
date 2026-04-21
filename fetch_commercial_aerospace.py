import requests
import json
import pandas as pd
from datetime import datetime
import os
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://q.10jqka.com.cn/',
    'Content-Type': 'application/json',
}

url = 'https://quota-h.10jqka.com.cn/fuyao/common_hq_aggr/quote/v1/multi_last_snapshot'

# 商业航天概念股票列表
commercial_aerospace_names = [
    '天马新材', '戈碧迦', '族兴新材', '长光华芯', '凯盛科技', '天通股份', '博云新材', '云南锗业',
    '广合科技', '江顺科技', '中瓷电子', '沃格光电', '安孚科技', '三安光电', '大业股份', '欧科亿',
    '侨源股份', '光库科技', '并行科技', '长盈通', '东材科技', '蜀道装备', '信维通信', '崧盛股份',
    '远航精密', '东方通信', '光弘科技', '星图测控', '锐科激光', '创远信科', '富士达', '万源通',
    '起帆电缆', '顺灏股份', '国博电子', '德龙激光', '新劲刚', '永贵电器', '优机股份', '苏轴股份',
    '新雷能', '罗博特科', '坤恒顺维', '广咨国际', '圣泉集团', '海特高新', '高德红外', '华光新材',
    '昊志机电', '广联航空', '澳弘电子', '有研复材', '天工股份', '银邦股份', '康达新材', '兴森科技',
    '火炬电子', '科强股份', '永鼎股份', '腾景科技', '航天电器', '七丰精工', '景旺电子', '一博科技',
    '多浦乐', '陕西华达', '莱赛激光', '天力复合', '金百泽', '宏发股份', '南山智尚', '奥普光电',
    '国睿科技', '本川智能', '科隆新材', '泰胜风能', '星辰科技', '华工科技', '斯瑞新材', '怡 亚 通',
    '鹿山新材', '广电计量', '雅达股份', '国力电子', '芯动联科', '昂瑞微-UW', '灿能电力', '华丰科技',
    '灿勤科技', '通宇通讯', '宏达电子', '国泰集团', '睿创微纳', '启明星辰', '海昌新材', '思泰克',
    '邵阳液压', '流金科技', '应流股份', '巨力索具', '科德数控', '航天长峰', '天润科技', '紫光国微',
    '泰嘉股份', '雷曼光电', '硕贝德', '楚江新材', '联创光电', '天成自控', '国瓷材料', '中京电子',
    '易事特', '生益科技', '明阳智能', '同益中', '翱捷科技-U', '卓胜微', 'ST惠伦', '西子洁能',
    '新益昌', '天银机电', '中钢洛耐', '集智股份', '恒辉安防', '远东股份', '鼎通科技', '泰永长征',
    '龙芯中科', '西部材料', '高凌信息', '经纬恒润-W', '金禄电子', '博敏电子', '立昂微', '隆华科技',
    '云汉芯城', '宏明电子', '东土科技', '理工导航', '聚和材料', '德恩精工', '有研粉材', '高华科技',
    '金天钛业', '久之洋', '国盛智科', '鹏鼎控股', '国科天成', '永新光学', '飞沃科技', '和顺电气',
    '中科星图', '安泰科技', '鸿远电子', '莱斯信息', '厦门象屿', '海兰信', '尤洛卡', '金风科技',
    '振芯科技', '合锻智能', '厦门钨业', '银河电子', '康斯特', '金发科技', '科新机电', '乾照光电',
    '中简科技', '太力科技', '苏州高新', '普利特', '矩子科技', '武汉凡谷', '盛帮股份', '福光股份',
    '航宇微', '蓝思科技', '海格通信', '瑞可达', '烽火通信', '安路科技', '司南导航', '瑞华泰',
    '利亚德', '航天晨光', '航天智装', '雷电微力', '沃特股份', '信音电子', '航天电子', '国机精工',
    '航天动力', '上海瀚讯', '电科蓝天', '大族激光', '光威复材', '北化股份', '金信诺', '崇达技术',
    '航天科技', '四创电子', '东方钽业', '中国船舶', '成都华微', '润贝航科', '中材科技', '北信源',
    '太钢不锈', '华测检测', '中船防务', '优刻得-W', '国芯科技', '天邑股份', '安达维尔', '中国联通',
    '天宜新材', '*ST大立', '航天环宇', '金帝股份', '天奥电子', '宜通世纪', '四川九洲', '中光防雷',
    '中衡设计', '中国长城', '新疆交建', '中核科技', '中国一重', '电科芯片', '信科移动-U', '南京化纤',
    '国林科技', '盛洋科技', '蓝盾光电', '航天软件', '神宇股份', '龙溪股份', '派克新材', '城建发展',
    '华如科技', '铂力特', '精工科技', '数码视讯', '博威合金', '西测测试', '南钢股份', '普天科技',
    '钢研高纳', '科力远', '中国卫星', '中天科技', '卡倍亿', '泰尔股份', '亚光科技', '宝钛股份',
    '旭升集团', '全信股份', '国电南自', '佳驰科技', '中瑞股份', '中泰股份', '广和通', '博亚精工',
    '先锋精科', '世运电路', '上海沪工', '高新兴', '航宇科技', '领益智造', '旷达科技', '大唐电信',
    '抚顺特钢', '中国电信', '苏试试验', '北摩高科', '三未信安', '泛亚微透', '霍莱沃', '硅宝科技',
    '双飞集团', '盛路通信', '万丰万威', '北路智控', '肯特股份', '北斗星通', '广东宏大', '隆基机械',
    '中国卫通', '振华风光', '电科网安', '成飞集成', '华力创通', '佳缘科技', '东华测试', '中国海防',
    '沈阳机床', '上大股份', '震有科技', '众合科技', '天合光能', '中航光电', '烽火电子', '利君股份',
    '国光电气', '能科科技', 'ST思科瑞', '上海港湾', '中研股份', '明志科技', '海能达', '科蓝软件',
    '必创科技', '西宁特钢', 'ST太重', '宏鑫科技', '中航成飞', '盟升电子', '日联科技', '*ST观典',
    '振华科技', '隆盛科技', '国科军工', '神开股份', '立中集团', '豪能股份', '万通发展', '创元科技',
    '爱科科技', '华测导航', '南京熊猫', '中国软件', '中信重工', '中国电建', '中兴通讯', '中航西飞',
    '华伍股份', '中兵红箭', '四维图新', '迈信林', '腾达科技', '光启技术', '中航机载', '九鼎新材',
    '佳讯飞鸿', '联建光电', '亚太科技', '新余国科', '佰奥智能', '千方科技', '七一二', '宗申动力',
    '观想科技', '西部超导', '*ST天微', '格林精密', '星网宇达', '宝武镁业', '深 赛 格', '金盾股份',
    '美格智能', '超声电子', '湘电股份', '贵绳股份', '凌云股份', '中国铁建', '大连重工', '东方中科',
    '中亦科技', '航发控制', '三棵树', '国瑞科技', '科顺股份', '中复神鹰', '弘信电子', '顶固集创',
    '智明达', '臻镭科技', '东方日升', '五洲新春', '金隅集团', '金宏气体', '中信特钢', '雷科防务',
    '长缆科技', '飞亚达', '合众思壮', '探路者', '招标股份', '风语筑', '和而泰', '深圳新星', '亚信安全',
    '宏英智能', '豪美新材', '超图软件', '当虹科技', '海信视像', '广汽集团', '兰石重装', '中航高科',
    '帝科股份', '龙建股份', '大元泵业', '江苏神通', '铭普光磁', '国检集团', '天融信', '中科环保',
    '融发核电', '电科数字', '九丰能源', '长江通信', '佳华科技', '新晨科技', '天箭科技', '中天火箭',
    '超捷股份', '*ST新研', '梅安森', 'ST创意', '谱尼测试', '中航重机', '昊华科技', '金明精机',
    'TCL中环', '旋极信息', '风华高科', '中超控股', '钧达股份', '酒钢宏兴', '四川金顶', '雪迪龙',
    '江航装备', '森源电气', '吉大正元', '中国交建', '杭氧股份', '上海艾录', '永信至诚', '航材股份',
    '川仪股份', '嘉环科技', '魅视科技', '陕鼓动力', '麒麟信安', '长城电工', '雪人集团', '阿特斯',
    '昇辉科技', '首都在线', '富瑞特装', '三维天地', '祥明智能', '中密控股', '春晖智控', '华曙高科',
    '航天发展', '浩瀚深度', '亿纬锂能', '拓日新能', '华菱线缆', '索辰科技', '再升科技', '振江股份',
    '盛邦安全', '三角防务', '红板科技', '湖南海利', 'ST达华', '深桑达Ａ', '丝路视觉', '航天宏图',
    '中环海陆', '神剑股份', '广钢气体', '红相股份', '国盾量子', '科大国创', '大名城', '*ST铖昌',
    '通光线缆', '直真科技', '中集集团', '新 和 成', '易天股份', '鼎龙科技'
]

# 从gp_codes.py获取股票代码
print('获取商业航天概念股票代码...')

# 读取gp_codes.py获取代码映射
with open('d:/kx724/gp_codes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 提取股票代码映射
code_map = {}
pattern = r"\{'代码':\s*'(\d+)',\s*'名称':\s*'([^']+)'"
for match in re.finditer(pattern, content):
    code_map[match.group(2)] = match.group(1)

# 获取商业航天股票代码
sh_codes = []
sz_codes = []
bj_codes = []

for name in commercial_aerospace_names:
    if name in code_map:
        code = code_map[name]
        if code.startswith('6'):
            sh_codes.append(code)
        elif code.startswith('0') or code.startswith('3'):
            sz_codes.append(code)
        elif code.startswith('8') or code.startswith('4') or code.startswith('9'):
            bj_codes.append(code)
    else:
        print(f'未找到股票代码: {name}')

code_list = []
if sh_codes:
    code_list.append({"market": "17", "codes": sh_codes})
if sz_codes:
    code_list.append({"market": "33", "codes": sz_codes})
if bj_codes:
    code_list.append({"market": "151", "codes": bj_codes})

payload = {
    "code_list": code_list,
    "trade_class": "intraday",
    "data_fields": ["55", "10", "199112", "264648", "19", "6"],
    "lang": "zh_cn",
    "gpid": 1
}

print(f'共获取到 {len(sh_codes) + len(sz_codes) + len(bj_codes)} 只股票代码')
print('获取商业航天概念板块数据...')

# 分批请求数据（每批最多50只股票）
def batch_request(all_codes, batch_size=50):
    stock_list = []
    for i in range(0, len(all_codes), batch_size):
        batch = all_codes[i:i+batch_size]
        batch_code_list = []
        sh_batch = [c for c in batch if c.startswith('6')]
        sz_batch = [c for c in batch if c.startswith(('0', '3'))]
        bj_batch = [c for c in batch if c.startswith(('8', '4', '9'))]
        if sh_batch:
            batch_code_list.append({"market": "17", "codes": sh_batch})
        if sz_batch:
            batch_code_list.append({"market": "33", "codes": sz_batch})
        if bj_batch:
            batch_code_list.append({"market": "151", "codes": bj_batch})
        
        batch_payload = {
            "code_list": batch_code_list,
            "trade_class": "intraday",
            "data_fields": ["55", "10", "199112", "264648", "19", "6"],
            "lang": "zh_cn",
            "gpid": 1
        }
        
        try:
            resp = requests.post(url, headers=headers, json=batch_payload, timeout=10)
            data = resp.json()
            quote_data = data.get('data', {}).get('quote_data', [])
            
            for item in quote_data:
                values = item.get('value', [])
                if not values:
                    continue
                v = values[0]
                price = v[5] if len(v) > 5 and v[5] is not None else 0
                change_pct = v[4] if len(v) > 4 and v[4] is not None else 0
                change = v[3] if len(v) > 3 and v[3] is not None else 0
                stock_list.append({
                    '代码': item.get('code', ''),
                    '名称': v[0],
                    '价格': float(price),
                    '涨跌幅': float(change_pct),
                    '涨跌': float(change),
                })
        except Exception as e:
            print(f'批次 {i//batch_size + 1} 请求失败: {e}')
    
    return stock_list

try:
    all_codes = sh_codes + sz_codes + bj_codes
    stock_list = batch_request(all_codes)
    
    # 创建DataFrame
    df = pd.DataFrame(stock_list)
    
    if df.empty:
        print('未获取到任何股票数据')
        exit()
    
    # 剔除ST股票
    df = df[~df['名称'].str.contains('ST', na=False)]
    
    # 剔除科创板股票（688开头）和北交所股票（920开头）
    df = df[~df['代码'].str.startswith(('688', '920'))]
    
    # 按价格降序排列
    df = df.sort_values('价格', ascending=False).reset_index(drop=True)
    
    # 太空光伏分类
    space_solar = [
        '凯盛科技', '沃格光电', '三安光电', '鹿山新材', '明阳智能', '西子洁能',
        '乾照光电', '蓝思科技', '瑞华泰', '天合光能', '上海港湾', '东方日升',
        '帝科股份', 'TCL中环', '钧达股份', '上海艾录', '阿特斯', '拓日新能'
    ]
    
    # 太空算力分类
    space_compute = [
        '顺灏股份', '腾景科技', '蓝思科技', '优刻得-W', '领益智造', '千方科技', '浩瀚深度'
    ]
    
    # 卫星通讯分类
    satellite_comm = [
        '信维通信', '东方通信', '国博电子', '新劲刚', '罗博特科', '星辰科技', '华丰科技',
        '通宇通讯', '硕贝德', '中京电子', '久之洋', '莱斯信息', '武汉凡谷', '海格通信',
        '上海瀚讯', '航天科技', '电科芯片', '信科移动-U', '盛洋科技', '中国卫星', '高新兴',
        '盛路通信', '北斗星通', '华力创通', '震有科技', '七一二', '智明达', '臻镭科技',
        '和而泰', '天箭科技', '梅安森', '吉大正元', 'ST达华', '*ST铖昌'
    ]
    
    # 火箭回收分类
    rocket_recovery = [
        '泰胜风能', '巨力索具', '海兰信', '宜通世纪', '中衡设计', '*ST观典', '超捷股份'
    ]
    
    # 蓝剑航天分类
    blue_sword_aerospace = [
        '昊志机电', '广联航空', '航天电器', '应流股份', '巨力索具', '高华科技', '和顺电气',
        '金风科技', '大族激光', '派克新材', '铂力特', '中泰股份', '航宇科技', '上大股份',
        '国光电气', 'ST思科瑞', '盟升电子', '振华科技', '豪能股份', '顶固集创', '九丰能源',
        '超捷股份', '中航重机', '华菱线缆', '神剑股份'
    ]
    
    # 卫星测控分类
    satellite_control = [
        '星图测控', '航天电子', '航天环宇', '霍莱沃', '中国卫通', '佳缘科技',
        '雷科防务', '长江通信', '吉大正元', '航天发展'
    ]
    
    # 卫星遥感分类
    satellite_remote = [
        '航宇微', '航天环宇', '天融信'
    ]
    
    # 火箭发射分类
    rocket_launch = [
        '科强股份', '泰胜风能', '斯瑞新材', '邵阳液压', '高华科技', '飞沃科技', '利亚德',
        '航天晨光', '航天电子', '国机精工', '光威复材', '大族激光', '中材科技', '天宜新材',
        '铂力特', '精工科技', '中泰股份', '抚顺特钢', '振华风光', '东华测试', 'ST思科瑞',
        'ST太重', '国科军工', '九鼎新材', '佳讯飞鸿', '新余国科', '大连重工', '顶固集创',
        '九丰能源', '新晨科技', '超捷股份', '中天火箭', '四川金顶', '富瑞特装', '索辰科技',
        '广钢气体', '神剑股份'
    ]
    
    # 中科宇航分类
    cas_space = [
        '斯瑞新材', '高华科技', '飞沃科技', '航宇微', '派克新材', '航宇科技',
        '苏试试验', '豪能股份', '立中集团', '超捷股份', '航天宏图', '神剑股份'
    ]
    
    # 创建分类字典
    category_stocks = {
        '全部': df,
        '太空光伏': df[df['名称'].isin(space_solar)],
        '太空算力': df[df['名称'].isin(space_compute)],
        '卫星通讯': df[df['名称'].isin(satellite_comm)],
        '火箭回收': df[df['名称'].isin(rocket_recovery)],
        '蓝剑航天': df[df['名称'].isin(blue_sword_aerospace)],
        '卫星测控': df[df['名称'].isin(satellite_control)],
        '卫星遥感': df[df['名称'].isin(satellite_remote)],
        '火箭发射': df[df['名称'].isin(rocket_launch)],
        '中科宇航': df[df['名称'].isin(cas_space)],
    }
    
    # 打印分类统计
    print('\n分类统计:')
    for category, stocks_df in category_stocks.items():
        print(f'  {category}: {len(stocks_df)} 只')
    
    # 打印全部数据
    print('\n商业航天概念板块数据:')
    print('=' * 100)
    print(df.to_string(index=False))
    
    # 创建Excel文件
    date_str = datetime.now().strftime('%Y-%m-%d')
    output_dir = 'news_data'
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f'商业航天_{date_str}.xlsx')
    
    # 保存到Excel
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        for sheet_name, sheet_df in category_stocks.items():
            if len(sheet_df) > 0:
                sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f'\n已保存到: {filepath}')
    print(f'包含 {len(category_stocks)} 个sheet: {list(category_stocks.keys())}')
    
except Exception as e:
    print(f'获取数据失败: {e}')
    import traceback
    traceback.print_exc()
