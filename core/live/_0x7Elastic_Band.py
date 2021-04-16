# -*- coding: utf-8 -*-
import time
import grequests
import pandas as pd
import midas.bin.env as env
from midas.core.data.engine import main_session
import midas.core.data.models as models

target_symbols = [
    '000004',
    '600396',
    '600467',
    '600499',
    '600500',
    '600513',
    '600576',
    '600590',
    '600640',
    '600766',
    '600779',
    '600780',
    '600782',
    '600787',
    '600828',
    '600843',
    '600847',
    '600857',
    '600859',
    '600860',
    '600872',
    '600882',
    '600916',
    '600917',
    '600389',
    '600360',
    '600310',
    '600298',
    '300643',
    '300684',
    '300689',
    '300745',
    '300751',
    '300755',
    '300790',
    '300817',
    '300824',
    '300825',
    '300848',
    '600929',
    '300859',
    '300896',
    '300905',
    '300918',
    '300933',
    '300936',
    '300942',
    '600025',
    '600097',
    '600218',
    '600223',
    '600237',
    '300881',
    '300589',
    '601127',
    '601609',
    '603386',
    '603499',
    '603580',
    '603598',
    '603825',
    '603893',
    '603901',
    '603919',
    '603926',
    '603933',
    '603976',
    '603998',
    '605005',
    '605081',
    '605111',
    '605116',
    '605118',
    '605151',
    '605158',
    '605218',
    '605228',
    '605258',
    '605303',
    '603383',
    '603366',
    '603348',
    '603336',
    '601611',
    '601798',
    '601866',
    '601919',
    '601956',
    '603002',
    '603032',
    '603076',
    '603080',
    '603095',
    '603106',
    '601339',
    '603110',
    '603123',
    '603129',
    '603139',
    '603159',
    '603196',
    '603197',
    '603232',
    '603277',
    '603278',
    '603290',
    '603319',
    '603116',
    '605358',
    '300543',
    '300496',
    '002026',
    '002138',
    '002139',
    '002154',
    '002179',
    '002192',
    '002199',
    '002209',
    '002235',
    '002264',
    '002285',
    '002306',
    '002316',
    '002329',
    '002369',
    '002382',
    '002383',
    '002388',
    '002442',
    '002474',
    '002490',
    '002512',
    '002536',
    '002002',
    '000978',
    '000968',
    '000963',
    '000009',
    '000010',
    '000056',
    '000065',
    '000151',
    '000425',
    '000503',
    '000516',
    '000523',
    '000559',
    '000605',
    '002549',
    '000616',
    '000797',
    '000799',
    '000825',
    '000851',
    '000881',
    '000883',
    '000899',
    '000919',
    '000920',
    '000936',
    '000959',
    '000720',
    '300516',
    '002580',
    '002654',
    '003000',
    '003003',
    '003004',
    '003009',
    '003016',
    '003025',
    '003028',
    '003031',
    '003032',
    '003035',
    '300023',
    '300061',
    '300094',
    '300100',
    '300172',
    '300228',
    '300272',
    '300290',
    '300329',
    '300458',
    '300465',
    '300471',
    '300486',
    '002999',
    '002996',
    '002995',
    '002969',
    '002655',
    '002659',
    '002662',
    '002677',
    '002682',
    '002693',
    '002696',
    '002699',
    '002738',
    '002756',
    '002765',
    '002646',
    '002769',
    '002824',
    '002850',
    '002857',
    '002875',
    '002881',
    '002885',
    '002901',
    '002913',
    '002931',
    '002955',
    '002962',
    '002774',
    '605388',
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
                    chg = (current_price / yesterday_closing_price - 1)
                    chg_display = '{}%'.format(round(chg*100, 2))
                    circ_mv = stock_map[code]['circ_mv']
                    local_high = float(stock_map[code]['local_high'])
                    fall_chg = (current_price / local_high - 1) * 100

                    if name == '苏美达':
                        print()

                    if_display = False
                    if (chg > 0) and (current_price > today_open) and (-10 < fall_chg < 0):
                        if_display = True

                    if if_display:
                        displays.append({
                            'note': '{code}\t{name}\tchg:{chg}\tfall_chg:{fall_chg}%\tprice:{price}\tcirc_mv:{circ_mv}亿'.format(code=code, name=name, chg=chg_display,
                                fall_chg=round(fall_chg, 2), price=round(current_price, 2), circ_mv=int(circ_mv)),
                            'fall_chg': fall_chg
                        })

            displays.sort(key=lambda x: x['fall_chg'], reverse=True)
            displays = displays[-10:]
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