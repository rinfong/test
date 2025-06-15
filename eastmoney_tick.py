# -*- coding: utf-8 -*-
import requests
import pandas as pd

def mark_bs_type(x):
    if x == 1 or x == '1':
        return 'sell'
    elif x == 2 or x == '2':
        return 'buy'
    else:
        return x

def split_market_code(sec_code):
    code_arr = sec_code.split('.')
    if len(code_arr) > 1:
        code = code_arr[0]
        market = code_arr[1]
        if market == 'SZ':
            market = 0
        elif market == 'SH':
            market = 1
        else:
            market = 2
        return market, code
    else:
        return -1, sec_code

def get_em_code(symbol):
    """
    生成东方财富股票专用的行情ID
    code:可以是代码或简称或英文
    返回格式：1.513100
    """
    symbol = str(symbol).split('.')[0]
    url = 'https://searchapi.eastmoney.com/api/suggest/get'
    params = (
        ('input', f'{symbol}'),
        ('type', '14'),
        ('token', 'D43BF722C8E33BDC906FB84D85E326E8'),
    )
    try:
        res = requests.get(url, params=params).json()
        code_dict = res['QuotationCodeTable']['Data']
        if code_dict:
            return code_dict[0]['QuoteID']
        else:
            print('输入东财代码有误')
    except Exception as e:
        print('获取东财代码报错', e)
        market, code = split_market_code(symbol)
        return f'{market}.{code}'

def get_sec_tick_em(sec_code):
    code_arr = sec_code.split('.')
    if len(code_arr) == 1:
        em_code = get_em_code(sec_code)
    else:
        market, code = split_market_code(sec_code)
        em_code = str(market) + '.' + str(code)
    url = 'https://push2.eastmoney.com/api/qt/stock/details/get?'
    params = {
        'secid': em_code,
        'forcect': '1',
        'invt': '2',
        'pos': -10000,
        'iscca': '1',
        'fields1': 'f1,f2,f3,f4,f5',
        'fields2': 'f51,f52,f53,f54,f55',
        'ut': 'f057cbcbce2a86e2866ab8877db1d059'
    }
    res = requests.get(url=url, params=params)
    text = res.json()['data']['details']
    data = []
    for item in text:
        data.append(item.split(','))
    df = pd.DataFrame(data)
    if len(df) > 0:
        df.columns = ['trade_time', 'price', 'volume', 'orders', 'bs']
        df['sec_code'] = sec_code
        df['price'] = pd.to_numeric(df['price'])
        df['volume'] = pd.to_numeric(df['volume'])
        df['amount'] = df['price'] * df['volume'] * 100
        df['orders'] = pd.to_numeric(df['orders'])
        df['bs'] = df['bs'].apply(mark_bs_type)
    return df

if __name__ == '__main__':
    # 示例：获取600519.SH的tick历史行情
    code = '600519.SH'
    df = get_sec_tick_em(code)
    df.to_csv(F'D:\{code}_TICK.csv', index=False, encoding='utf-8-sig')
    print(df)