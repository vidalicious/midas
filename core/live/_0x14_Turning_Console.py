# -*- coding: utf-8 -*-
import sys
import os

live_path = os.path.dirname(os.path.realpath(__file__))
core_path = os.path.split(live_path)[0]
root_path = os.path.split(core_path)[0]
parent_path = os.path.split(root_path)[0]
sys.path.append(parent_path)

import time
import grequests
import pandas as pd
import midas.bin.env as env
from midas.core.data.engine import main_session
import midas.core.data.models as models
from bs4 import BeautifulSoup

target_symbols = [
    '300077',
    '002077',
    '300456',
    '300671',
    '300598',
    '002326',
    '600573',
    '300604',
    '002091',
    '002411',
    '300390',
    '002169',
    '000408',
    '000925',
    '600884',
    '300432',
    '603893',
    '600460',
    '300709',
    '300712',
    '002055',
    '300613',
    '300458',
    '002261',
    '000004',
    '002805',
    '600381',
    '300579',
    '300139',
    '600096',
    '300082',
    '002156',
    '603328',
    '300708',
    '002194',
    '300656',
    '300736',
    '300663',
    '300831',
    '002646',
    '300578',
    '002371',
    '300134',
    '300322',
    '600770',
    '300379',
    '603659',
    '603688',
    '002176',
    '300035',
    '600478',
    '600703',
    '600702',
    '300438',
    '300207',
    '600600',
    '300352',
    '600199',
    '300346',
    '300769',
    '300310',
    '603712',
    '300477',
    '300297',
    '002288',
    '300560',
    '603906',
    '002929',
    '605358',
    '600753',
    '300096',
    '300448',
    '603650',
    '300052',
    '002723',
    '600520',
    '002957',
    '300623',
    '300376',
    '300131',
    '002421',
    '600105',
    '300366',
    '603068',
    '600360',
    '300548',
    '002738',
    '300053',
    '603283',
    '000555',
    '603189',
    '002342',
    '300353',
    '002023',
    '000063',
    '603690',
    '300319',
    '002885',
    '300260',
    '600616'
]

target_symbols = list(set(target_symbols))

# def get_kaipanla_symbols(concept):
#     with open('{data_path}/{concept}.html'.format(data_path=env.data_path, concept=concept), "r") as f:  # 打开文件
#         text = f.read()  # 读取文
#     soup = BeautifulSoup(markup=text, features='lxml')
#     symbol_tags = soup.find_all(class_='c gray')
#
#     symbols = []
#     for tag in symbol_tags:
#         symbol = tag.get_text()
#         symbols.append(symbol)
#
#     return symbols
#
#
# def get_symbols():
#     symbol_set = set()
#     for concept in ['碳中和', '医美', '锂电池', '酿酒', '医药', '食品饮料']:
#         symbols = get_kaipanla_symbols(concept=concept)
#         for symbol in symbols:
#             symbol_set.add(symbol)
#
#     return list(symbol_set)

def get_intensity(close, today_open, pre_close):
    if abs(today_open - close) > abs(pre_close - close):
        chg = (close / today_open - 1) * 100
    else:
        chg = (close / pre_close - 1) * 100

    if chg > 9:
        intensity = 4
    elif chg > 6:
        intensity = 3
    elif chg > 3:
        intensity = 2
    elif chg > 0:
        intensity = 1
    elif chg > -3:
        intensity = -1
    elif chg > -6:
        intensity = -2
    elif chg > -9:
        intensity = -3
    else:
        intensity = -4

    return intensity

def run():
    # target_symbols = get_symbols()

    symbol2code = {}
    stock_map = {}

    for stock in main_session.query(models.DailyBasic).all():
        ts_code = stock.ts_code
        market = ts_code.split('.')[1].lower()
        symbol = ts_code.split('.')[0]
        name = stock.name
        code = '{market}{symbol}'.format(market=market, symbol=symbol)
        symbol2code[symbol] = code

        if symbol.startswith('300'):
            limit_rate = 0.2
        elif symbol.startswith('688'):
            limit_rate = 0.2
        elif 'ST' in name:
            limit_rate = 0.05
        else:
            limit_rate = 0.1

        stock_map[code] = {
            'circ_mv': float(stock.circ_mv),
            'limit_rate': limit_rate,
            'odds': -9999,
            'delta_odds': 9999
        }

    df = pd.read_csv('{data_path}/window_odds.csv'.format(data_path=env.data_path))
    for i in range(len(df)):
        ts_code = df.loc[i, 'ts_code']

        market = ts_code.split('.')[1].lower()
        symbol = ts_code.split('.')[0]
        code = '{market}{symbol}'.format(market=market, symbol=symbol)

        odds = df.loc[i, 'COL_ODDS']
        delta_odds = df.loc[i, 'COL_DELTA_ODDS']
        stock_map[code]['odds'] = odds
        stock_map[code]['delta_odds'] = delta_odds

    batch_size = 500
    req_list = []
    for i in range(0, len(target_symbols), batch_size):
        keys = []
        for symbol in target_symbols[i:i+batch_size]:
            query_key = symbol2code[symbol]
            keys.append(query_key)

        req_list.append(grequests.get('http://hq.sinajs.cn/list={}'.format(','.join(keys))))

    while True:
        time_a = time.time()
        try:
            responses = grequests.map(req_list)
            print('====== {} ======'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            displays = []
            for response in responses:
                res = response.text.strip().split(';\n')
                for i in res:
                    j = i.split(',')
                    name = j[0].split('="')[1]
                    code = j[0].split('="')[0].split('_')[-1]
                    today_open_price = float(j[1])
                    yesterday_closing_price = float(j[2])
                    current_price = float(j[3])
                    today_max_price = float(j[4])
                    buy_one_price = float(j[6])
                    buy_one_vol = float(j[10])
                    limit_rate = stock_map[code]['limit_rate']
                    today_limit_price = round(yesterday_closing_price * (1 + limit_rate), 2)
                    chg = (current_price / yesterday_closing_price - 1)
                    chg_display = '{}%'.format(round(chg*100, 2))
                    # circ_mv = stock_map[code]['circ_mv']
                    odds = stock_map[code]['odds']
                    delta_odds = stock_map[code]['delta_odds']
                    today_intensity = get_intensity(close=current_price, today_open=today_open_price, pre_close=yesterday_closing_price)
                    # intensity_variety = today_intensity - past_intensity

                    if_display = False
                    if (today_limit_price > buy_one_price) and (today_intensity > 0) and (delta_odds < 0):
                    # if today_limit_price > buy_one_price and past_intensity < -1:
                        if_display = True

                    if if_display:
                        displays.append({
                            'note': '{code}\t{name}\tchg:{chg}\tprice:{price}\todds:{odds}\tdelta_odds:{delta_odds}'.format(code=code, name=name, chg=chg_display,
                                price=round(current_price, 2), intensity=today_intensity, odds=odds, delta_odds=delta_odds),
                            'odds': odds,
                            'delta_odds': delta_odds
                        })

            displays.sort(key=lambda x: x['odds'], reverse=False)
            displays = displays[-20:]
            notes = [i['note'] for i in displays]
            print('\n'.join(notes))
        except Exception as e:
            print(e)
            continue
        time_b = time.time()
        cost = time_b - time_a
        time.sleep(1 - cost)


if __name__ == '__main__':
    run()