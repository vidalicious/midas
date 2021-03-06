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

target_symbols = [
    '000820',
    '600078',
    '000980',
    '600122',
    '600816',
    '002256',
    '002684',
    '600615',
    '601020',
    '603157'
]

blacklist_symbols = [
    '000820',
    '000980'
]

t_set = set()
for symbol in target_symbols:
    if symbol not in blacklist_symbols:
        t_set.add(symbol)

target_symbols = list(t_set)

pass

def run():

    symbol2code = {}
    stock_map = {}
    for stock in main_session.query(models.DailyBasic).all():
        ts_code = stock.ts_code
        market = ts_code.split('.')[1].lower()
        symbol = ts_code.split('.')[0]
        code = '{market}{symbol}'.format(market=market, symbol=symbol)
        symbol2code[symbol] = code
        stock_map[code] = {
            'circ_mv': float(stock.circ_mv)
        }

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
                    yesterday_closing_price = float(j[2])
                    current_price = float(j[3])
                    today_max_price = float(j[4])
                    buy_one_price = float(j[6])
                    buy_one_vol = float(j[10])
                    today_limit_price = round(yesterday_closing_price * 1.05, 2)
                    chg = (current_price / yesterday_closing_price - 1)
                    chg_display = '{}%'.format(round(chg*100, 2))
                    circ_mv = stock_map[code]['circ_mv']

                    if_display = False
                    type = 1
                    if today_max_price == today_limit_price: #摸过板的
                        if_display = True
                        if buy_one_price < today_limit_price: #开板
                            if_display = True
                        elif buy_one_price * buy_one_vol < 10000000: #封单小于1kw
                            if_display = True
                            type = 2

                    elif chg > 0.025:
                        if_display = True

                    # if_display = True

                    if if_display:
                        if type == 2:
                            displays.append({
                                'note': '{code}\t{name}\tchg:{chg}\tprice:{price}\tcirc_mv:{circ_mv}亿\t封单:{vol}手'.format(code=code, name=name, chg=chg_display,
                                    price=round(current_price, 2), circ_mv=int(circ_mv), vol=int(buy_one_vol / 100)),
                                'chg': chg
                            })
                        else:
                            displays.append({
                                'note': '{code}\t{name}\tchg:{chg}\tprice:{price}\tcirc_mv:{circ_mv}亿'.format(code=code, name=name, chg=chg_display,
                                    price=round(current_price, 2), circ_mv=int(circ_mv)),
                                'chg': chg
                            })

            displays.sort(key=lambda x: x['chg'], reverse=False)
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