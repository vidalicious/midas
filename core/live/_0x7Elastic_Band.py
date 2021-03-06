# -*- coding: utf-8 -*-
import time
import grequests
import pandas as pd
import midas.bin.env as env
from midas.core.data.engine import main_session
import midas.core.data.models as models

target_symbols = [
    '300093',
    '002222',
    '300339',
    '002670',
    '300928',
    '002229',
    '002241',
    '002590',
    '000430',
    '002273',
    '002176',
    '601238',
    '000700',
    '603290',
    '002036',
    '002709',
    '603799',
    '002428',
    '603955',
    '002997',
    '002664',
    '000868',
    '603333',
    '603316',
    '002460',
    '600660',
    '601882',
]

target_symbols = list(set(target_symbols))

daily001 = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == '000001.SZ').order_by(models.DailyPro.trade_date.desc()).all()
LAST_MARKET_DATE = daily001[0].trade_date

def run():

    symbol2code = {}
    stock_map = {}
    for stock in main_session.query(models.DailyBasic).all():
        ts_code = stock.ts_code
        market = ts_code.split('.')[1].lower()
        symbol = ts_code.split('.')[0]
        code = '{market}{symbol}'.format(market=market, symbol=symbol)
        symbol2code[symbol] = code
        if symbol in target_symbols:
            stock_map[code] = {
                'circ_mv': float(stock.circ_mv),
                'ts_code': ts_code
            }

    for symbol in target_symbols:
        code = symbol2code[symbol]
        ts_code = stock_map[code]['ts_code']
        daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == ts_code,
                                                           models.DailyPro.trade_date <= LAST_MARKET_DATE).order_by(
            models.DailyPro.trade_date.desc()).limit(10).all()
        local_high = local_max_high(daily, local_scale=5)
        stock_map[code]['local_high'] = local_high
        print('=== pass {} ==='.format(symbol))


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
                    today_open = float(j[1])
                    yesterday_closing_price = float(j[2])
                    current_price = float(j[3])
                    today_high = float(j[4])
                    chg = (current_price / yesterday_closing_price - 1)
                    chg_display = '{}%'.format(round(chg*100, 2))
                    circ_mv = stock_map[code]['circ_mv']
                    # local_high = float(stock_map[code]['local_high'])
                    fall_chg = (current_price / today_high - 1) * 100

                    if_display = False
                    # if (chg > 0) and (current_price > today_open) and (-10 < fall_chg < 0):
                    #     if_display = True

                    if (chg < 0) and (current_price < today_open):
                        if_display = True

                    if if_display:
                        displays.append({
                            'note': '{code}\t{name}\tchg:{chg}\tfall_chg:{fall_chg}%\tprice:{price}\tcirc_mv:{circ_mv}亿'.format(code=code, name=name, chg=chg_display,
                                fall_chg=round(fall_chg, 2), price=round(current_price, 2), circ_mv=int(circ_mv)),
                            'chg': chg,
                            'fall_chg': fall_chg,
                            'circ_mv': circ_mv
                        })

            displays.sort(key=lambda x: x['circ_mv'], reverse=True)
            # displays = displays[-10:]
            notes = [i['note'] for i in displays]
            print('\n'.join(notes))
        except Exception as e:
            print(e)
            continue
        time_b = time.time()
        cost = time_b - time_a
        time.sleep(1 - cost)


def local_max_high(sequence=None, local_scale=5):
    sequence = sequence[:local_scale]
    high = 0
    for item in sequence:
        high = max(high, item.high)
    return high



if __name__ == '__main__':
    run()