import akshare as ak

# 测试akshare新浪接口
print('测试akshare新浪接口...')

# 获取新浪实时行情
try:
    df = ak.stock_zh_a_spot()
    print(f'stock_zh_a_spot: {df.columns.tolist()}')
    print(df.head(3))
except Exception as e:
    print(f'stock_zh_a_spot 错误: {e}')

print('\n' + '='*50 + '\n')

# 获取新浪财务指标
try:
    df = ak.stock_financial_analysis_indicator(symbol="600519")
    print(f'stock_financial_analysis_indicator: {df.columns.tolist()}')
    print(df.head(3))
except Exception as e:
    print(f'stock_financial_analysis_indicator 错误: {e}')
