import sys
sys.path.insert(0, 'd:\\kx724')
from news_scraper import NewsScraper
from concept_codes import concept_map

# 测试所有概念代码
scraper = NewsScraper()

print(f"总共需要测试 {len(concept_map)} 个概念代码\n")

# 按类别分组测试
categories = {
    'AI/人工智能': ['人工智能', 'AI应用', 'AI智能体', 'AIGC概念', 'ChatGPT概念', 'AI PC', 'AI眼镜', 'AI语料', '中国AI 50', 'DeepSeek概念', '大模型', '算力', '算力租赁', 'CPO概念'],
    '芯片/半导体': ['芯片概念', '半导体', '第三代半导体', '光刻机', '光刻胶', '芯片设计', '封装测试', '存储芯片', '模拟芯片', '功率半导体', 'MCU芯片', '射频芯片', '传感器'],
    '机器人/智能制造': ['机器人', '人形机器人', '工业机器人', '机器视觉'],
    '数字经济/数据要素': ['数字经济', '数据要素', '大数据', '云计算', '东数西算', '国产软件', '操作系统', '鸿蒙概念', '华为概念'],
    '通信/5G/卫星': ['通信', '5G', '卫星导航', '卫星互联网', '商业航天', '低空经济', '无人机', '北斗导航'],
    '新能源': ['光伏', '风电', '储能', '电池', '钠离子电池', '固态电池', '氢能', '燃料电池', '充电桩', '智能电网', '虚拟电厂', '绿色电力', '核电', '可控核聚变'],
    '汽车': ['汽车', '新能源车', '车联网', '汽车电子', '一体化压铸', '华为汽车', '小米汽车'],
    '消费电子': ['消费电子', '智能手机', 'AI手机', '折叠屏', 'VR/AR', 'MR', '智能穿戴', '智能音箱'],
    '医药/医疗': ['医疗', '医药制造', '生物医药', '创新药', 'CXO', 'CRO概念', '中药', '医疗器械', '脑机接口', '合成生物', '基因测序', '减肥药', '辅助生殖'],
    '农业': ['农业', '种业', '转基因', '养殖', '饲料', '化肥', '农药', '数字乡村', '供销社'],
    '军工': ['军工', '航天', '船舶', '航空发动机', '航母', '北斗'],
    '资源能源': ['石油', '天然气', '煤炭', '有色金属', '黄金', '铜', '铝', '钢铁', '小金属'],
    '化工': ['化工', '磷化工', '硅化工', '煤化工', '塑料', '橡胶'],
    '金融': ['银行', '证券', '保险', '互联网金融', '数字货币', '金融科技', '多元金融', '期货'],
    '房地产/基建': ['房地产', '基建', '建材', '水泥', '玻璃', '装修', '物业', '新型城镇化', '城中村改造'],
    '消费': ['消费', '零售', '食品', '白酒', '啤酒', '饮料', '乳制品', '家电', '服装', '纺织', '旅游', '造纸', '化妆品', '珠宝', '家具', '鞋类', '预制菜', '免税'],
    '传媒/游戏': ['传媒', '游戏', '影视', '短剧', 'IP经济', '数字水印', '知识产权', '教育', '体育产业'],
    '环保/碳中和': ['环保', '碳交易', '节能环保', '固废处理'],
    '交通物流': ['港口', '航运', '集运', '交通', '铁路', '高速公路', '物流', '机场', '航空', '智能物流', '统一大市场'],
    '一带一路/自贸区': ['一带一路', '自贸区', '上海自贸区', '海南自贸区', '福建自贸区', '天津自贸区', '广东自贸区', '黑龙江自贸区', 'RCEP', '跨境支付', 'CIPS', '人民币贬值受益'],
    '国企改革': ['中字头', '中特估', '混合所有制', 'ST'],
    '区域概念': ['京津冀', '长三角', '横琴新区', '雄安新区', '成渝经济圈', '西部大开发', '东北振兴', '海南', '深圳', '浦东'],
    '其他热门概念': ['超导', '量子科技', '元宇宙', 'Web3.0', '数字人民币', '电子身份证', '培育钻石', '医美', '近视', '宠物', '银发经济', '托育服务'],
    '财报/业绩': ['业绩预增'],
    '市场风格': ['大盘价值', '小盘成长', '破净', '低价股', '次新股', '北交所', '创业板'],
    '新材料': ['新材料', '碳纤维', 'OLED', 'MiniLED', 'MicroLED', '柔性屏', '3D玻璃', '半导体材料'],
    '新基建': ['新基建', '5G基站', '城际高铁', '充电桩', '人工智能', '工业互联网'],
}

# 统计信息
total_tested = 0
total_success = 0
total_failed = 0
failed_concepts = []

# 按类别测试
for category, concepts in categories.items():
    print(f"\n{'='*60}")
    print(f"测试类别: {category} ({len(concepts)} 个概念)")
    print('='*60)
    
    category_success = 0
    category_failed = 0
    
    for concept in concepts:
        total_tested += 1
        code = concept_map.get(concept, '')
        
        try:
            # 测试新闻分析
            test_title = f"{concept}概念利好"
            test_content = f"{concept}概念受政策利好，相关概念股走强"
            
            result = scraper.analyze_news_stocks(test_title, test_content)
            
            if result and result.get('matched'):
                stock_count = len(result.get('stocks', []))
                industries = result.get('industries', [])
                
                # 检查是否匹配到正确的概念
                matched_correct = any(ind.get('name') == concept or concept in ind.get('name', '') for ind in industries)
                
                if matched_correct and stock_count > 0:
                    print(f"  ✓ {concept} ({code}): {stock_count} 只股票")
                    total_success += 1
                    category_success += 1
                else:
                    print(f"  ✗ {concept} ({code}): 匹配异常或无股票")
                    total_failed += 1
                    category_failed += 1
                    failed_concepts.append((concept, code, '匹配异常或无股票'))
            else:
                print(f"  ✗ {concept} ({code}): 未匹配")
                total_failed += 1
                category_failed += 1
                failed_concepts.append((concept, code, '未匹配'))
        except Exception as e:
            print(f"  ✗ {concept} ({code}): 错误 - {str(e)[:50]}")
            total_failed += 1
            category_failed += 1
            failed_concepts.append((concept, code, str(e)[:50]))
    
    print(f"\n{category} 测试结果: {category_success} 成功, {category_failed} 失败")

# 总结
print(f"\n{'='*60}")
print(f"测试总结")
print('='*60)
print(f"总测试数量: {total_tested}")
print(f"成功: {total_success}")
print(f"失败: {total_failed}")
print(f"成功率: {total_success/total_tested*100:.1f}%")

if failed_concepts:
    print(f"\n失败的概念列表:")
    for concept, code, reason in failed_concepts:
        print(f"  - {concept} ({code}): {reason}")
