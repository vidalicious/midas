# -*- coding: utf-8 -*-
import time
import grequests
import pandas as pd
import midas.bin.env as env
from midas.core.data.engine import main_session
import midas.core.data.models as models
from bs4 import BeautifulSoup

# target_symbols = list(set(target_symbols))

symbol_black_list = [

]

def get_kaipanla_symbols():
    with open('{data_path}/kaipanla_stuffs.html'.format(data_path=env.data_path), "r") as f:  # 打开文件
        text = f.read()  # 读取文
    soup = BeautifulSoup(markup=text, features='lxml')
    symbol_tags = soup.find_all(class_='c gray')

    symbols = []
    for tag in symbol_tags:
        symbol = tag.get_text()
        symbols.append(symbol)

    return symbols

def run():
    target_symbols = []

    kaipanla_symbols = get_kaipanla_symbols()

    kaipanla_symbols = list(set(kaipanla_symbols))

    df = pd.read_csv('{data_path}/silent_ones.csv'.format(data_path=env.data_path))
    for i in range(len(df)):
        ts_code = df.loc[i, 'ts_code']
        symbol = ts_code.split('.')[0]

        if symbol not in symbol_black_list and symbol in kaipanla_symbols:
            target_symbols.append(symbol)

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
                    today_limit_price = round(yesterday_closing_price * 1.1, 2)
                    chg = (current_price / yesterday_closing_price - 1)
                    chg_display = '{}%'.format(round(chg*100, 2))
                    circ_mv = stock_map[code]['circ_mv']

                    if_display = False
                    type = 1
                    desc = ''
                    if today_max_price == today_limit_price: #摸过板的
                        if buy_one_price < today_limit_price: #开板
                            if_display = True
                        elif buy_one_price * buy_one_vol < 10000000: #封单小于1kw
                            if_display = True
                            type = 2

                    elif chg > 0:
                        if_display = True
                        desc += '未上板'

                    if if_display:
                        if type == 2:
                            displays.append({
                                'note': '{code}\t{name}\tchg:{chg}\tprice:{price}\tcirc_mv:{circ_mv}亿\t封单:{vol}手'.format(code=code, name=name, chg=chg_display,
                                    price=round(current_price, 2), circ_mv=int(circ_mv), vol=int(buy_one_vol / 100)),
                                'chg': chg
                            })
                        else:
                            displays.append({
                                'note': '{code}\t{name}\tchg:{chg}\tprice:{price}\tcirc_mv:{circ_mv}亿\t{desc}'.format(code=code, name=name, chg=chg_display,
                                    price=round(current_price, 2), circ_mv=int(circ_mv), desc=desc),
                                'chg': chg
                            })

            displays.sort(key=lambda x: x['chg'], reverse=True)
            displays = displays[:5]
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