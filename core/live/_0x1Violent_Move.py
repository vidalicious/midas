# -*- coding: utf-8 -*-
import time
import grequests
import midas.bin.env as env


def run():
    stocks = []
    stock_map = {}
    for i in open('{data_path}/silent_ones'.format(data_path=env.data_path)):
        infos = i.strip().split(',')
        stocks.append({
            'name': infos[0],
            'symbol': infos[1],
            'market': infos[2]
        })
        stock_map['{market}{symbol}'.format(market=infos[2], symbol=infos[1])] = float(infos[3])


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
                    local_max = stock_map[code]
                    if 0.05 < chg < 0.098:
                        if current_price > local_max:
                            local_breaks.append({
                                'note': 'local break\t{code}\t{name}\tchg:{chg}\tprice:{price}'.format(code=code, name=name, chg=chg_display, price=round(current_price, 2)),
                                'chg': chg
                            })
                        else:
                            # print('violent move\t{code}\t{name}\tchg:{chg}\tprice:{price}'.format(code=code, name=name, chg=chg_display, price=round(current_price, 2)))
                            pass
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