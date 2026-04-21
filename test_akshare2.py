import akshare as ak

# 测试akshare财务指标接口
print('测试akshare财务指标接口...')

# 获取新浪财务指标
try:
    df = ak.stock_financial_report_sina(stock="600519", symbol="资产负债表")
    print(f'stock_financial_report_sina 资产负债表: {df.columns.tolist()}')
except Exception as e:
    print(f'stock_financial_report_sina 错误: {e}')

print('\n' + '='*50 + '\n')

# 获取新浪财务指标
try:
    df = ak.stock_financial_report_sina(stock="600519", symbol="利润表")
    print(f'stock_financial_report_sina 利润表: {df.columns.tolist()}')
except Exception as e:
    print(f'stock_financial_report_sina 利润表 错误: {e}')

print('\n' + '='*50 + '\n')

# 获取新浪财务指标
try:
    df = ak.stock_financial_report_sina(stock="600519", symbol="现金流量表")
    print(f'stock_financial_report_sina 现金流量表: {df.columns.tolist()}')
except Exception as e:
    print(f'stock_financial_report_sina 现金流量表 错误: {e}')

print('\n' + '='*50 + '\n')

# 获取新浪财务摘要
try:
    df = ak.stock_financial_abstract_sina(stock="600519")
    print(f'stock_financial_abstract_sina: {df.columns.tolist()}')
    print(df.head())
except Exception as e:
    print(f'stock_financial_abstract_sina 错误: {e}')
