# -*- coding: utf-8 -*-
import time
import grequests
import pandas as pd
import midas.bin.env as env


def run():
    stocks = []
    stock_map = {}
    df = pd.read_csv('{data_path}/live_oneplus.csv'.format(data_path=env.data_path))
    for i in range(len(df)):
        ts_code = df.loc[i, 'ts_code']
        if ts_code.startswith('688'):
            continue

        market = ts_code.split('.')[1].lower()
        symbol = ts_code.split('.')[0]
        name = df.loc[i, 'name']
        stocks.append({
            'name': name,
            'symbol': symbol,
            'market': market
        })
        stock_map['{market}{symbol}'.format(market=market, symbol=symbol)] = {
            'local_max': float(df.loc[i, 'COL_DAILY_LOCAL_MAX']),
            'circ_mv': float(df.loc[i, 'COL_CIRC_MV'])
        }


    batch_size = 500
    req_list = []
    for i in range(0, len(stocks), batch_size):
        keys = []
        for item in stocks[i:i+batch_size]:
            query_key = '{market}{symbol}'.format(market=item['market'], symbol=item['symbol'])
            keys.append(query_key)

        req_list.append(grequests.get('http://hq.sinajs.cn/list={}'.format(','.join(keys))))

    while True:
        time_a = time.time()
        try:
            responses = grequests.map(req_list)
            print('====== {} ======'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            local_breaks = []
            for response in responses:
                res = response.text.strip().split(';\n')
                for i in res:
                    j = i.split(',')
                    name = j[0].split('="')[1]
                    code = j[0].split('="')[0].split('_')[-1]
                    yesterday_closing_price = float(j[2])
                    current_price = float(j[3])
                    chg = (current_price / yesterday_closing_price - 1)
                    chg_display = '{}%'.format(round(chg*100, 2))
                    circ_mv = stock_map[code]['circ_mv']
                    # if 0.05 < chg < 0.098 and current_price > local_max:
                    if 0.05 < chg:
                        local_breaks.append({
                            'note': '{code}\t{name}\tchg:{chg}\tprice:{price}\tcirc_mv:{circ_mv}亿'.format(code=code, name=name, chg=chg_display,
                                price=round(current_price, 2), circ_mv=int(circ_mv / 10000)),
                            'chg': chg
                        })

            local_breaks.sort(key=lambda x: x['chg'], reverse=False)
            notes = [i['note'] for i in local_breaks]
            print('\n'.join(notes))
        except Exception as e:
            print(e)
            continue
        time_b = time.time()
        cost = time_b - time_a
        time.sleep(1 - cost)


if __name__ == '__main__':
    run()