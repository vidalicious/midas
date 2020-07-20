# -*- coding: utf-8 -*-
import os
import pickle
import pandas as pd
import time
import grequests
import midas.bin.env as env


def run():
    stocks = []
    stock_map = {}
    df = pd.read_csv('{data_path}/for_lives.csv'.format(data_path=env.data_path))
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
            'accumulation_aggressive': float(df.loc[i, 'COL_ACCUMULATION_AGGRESSIVE'])
        }

    # for i in open('{data_path}/silent_ones'.format(data_path=env.data_path)):
    #     infos = i.strip().split(',')
    #     if infos[1].startswith('688'):
    #         continue
    #     stocks.append({
    #         'name': infos[0],
    #         'symbol': infos[1],
    #         'market': infos[2]
    #     })
    #     stock_map['{market}{symbol}'.format(market=infos[2], symbol=infos[1])] = {
    #         'local_max': float(infos[3])
    #     }


    big_hands = {}
    time_str = time.strftime("%Y-%m-%d", time.localtime())
    pickle_file_name = '{buffer_path}/{time_str}@big_hand.pkl'.format(buffer_path=env.buffer_path, time_str=time_str)
    if os.path.exists(pickle_file_name):
        with open(pickle_file_name, 'rb') as file:
            try:
                big_hands = pickle.load(file)
            except EOFError:
                big_hands = {}

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
                    local_max = stock_map[code]['local_max']
                    vols = int(j[8]) / 100
                    # update
                    if 'vols' in stock_map[code]:
                        last_vols = stock_map[code]['vols']
                        delta_vols = vols - last_vols
                    else:
                        # first time
                        stock_map[code]['vols'] = vols
                        delta_vols = 0

                    if delta_vols >= 10000:
                        if code not in big_hands:
                            big_hands[code] = {
                                'max_delta_vols': delta_vols
                            }
                        if delta_vols > big_hands[code]['max_delta_vols']:
                            big_hands[code]['max_delta_vols'] = delta_vols

                            with open(pickle_file_name, 'wb') as file:
                                pickle.dump(big_hands, file)


                    if current_price > local_max and 0.05 < chg < 0.098 and code in big_hands:
                        local_breaks.append({
                            'note': 'local break\t{code}\t{name}\tchg:{chg}\tprice:{price}\tbig_hands:{big_hands}\t\taccumulation:{accumulation}'.format(
                                code=code, name=name, chg=chg_display, price=round(current_price, 2), big_hands=int(big_hands[code]['max_delta_vols']),
                                accumulation=round(stock_map[code]['accumulation_aggressive'], 2)),
                            'chg': chg
                        })
                    #
                    # if 0.05 < chg < 0.098:
                    #     if current_price > local_max:
                    #         local_breaks.append({
                    #             'note': 'local break\t{code}\t{name}\tchg:{chg}\tprice:{price}'.format(code=code, name=name, chg=chg_display, price=round(current_price, 2)),
                    #             'chg': chg
                    #         })
                    #     else:
                    #         # print('violent move\t{code}\t{name}\tchg:{chg}\tprice:{price}'.format(code=code, name=name, chg=chg_display, price=round(current_price, 2)))
                    #         pass
            local_breaks.sort(key=lambda x: x['chg'], reverse=True)
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