# -*- coding: utf-8 -*-
import requests
import time
import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.midas.analyzer.api as api

import midas.midas.data.models as models
from midas.midas.data.engine import main_session


def main():
    date = time.strftime("%Y-%m-%d", time.localtime())
    f = open('../../logs/{date}@liveshow.txt'.format(date=date), 'a', encoding='utf8')
    f_note = open('../../logs/{date}@liveshow_note.txt'.format(date=date), 'a', encoding='utf8')
    while int(time.strftime("%H%M%S", time.localtime())) < 92500:
        print('sleep for 5 secs, {}'.format(time.strftime("%H:%M:%S", time.localtime())))
        time.sleep(5)

    while int(time.strftime("%H%M%S", time.localtime())) < 94000:
        for i, stock_basic in enumerate(main_session.query(models.StockBasicPro).all()):
            try:
                query_key = '{a}{b}'.format(a=stock_basic.ts_code.split('.')[1].lower(), b=stock_basic.symbol)
                response = requests.get('http://hq.sinajs.cn/list={}'.format(query_key))
                res = response.text.split(',')
                chg = round((float(res[3]) / float(res[2]) - 1) * 100, 2)
                formatted = '{index} {code} {name} 今开:{open} 昨收:{yesterday} 当前百分比:{chg} 当前:{current} 成交股数:{stocks} 成交额:{amount} {date} ' \
                            '{timestamp}\n'.format(index=i, code=stock_basic.ts_code, name=stock_basic.name, open=res[1],
                                                 yesterday=res[2],
                                                 chg=chg, current=res[3], stocks=res[8], amount=res[9], date=res[30],
                                                 timestamp=res[31])
                f.write(formatted)
                print(formatted)

                time_int = int(time.strftime("%H%M%S", time.localtime()))
                if time_int < 93000 and chg > 4 and float(res[9]) > 50000000:
                    f_note.write(formatted)
            except Exception as e:
                print('excetion in index:{index} {code} {name}'.format(index=i, code=stock_basic.ts_code,
                                                                       name=stock_basic.name))
                continue

        f.write('\n############################################################################\n\n')
        f_note.write('\n############################################################################\n\n')
    f.close()
    f_note.close()

# value = requests.get('http://hq.sinajs.cn/list=sz000001')
# a = value.text.split(',')
# formatted = '{code} {name} 今开:{open} 昨收:{yesterday} 当前:{current} 成交股数:{stocks} 成交额:{amount} {date} ' \
#             '{timestamp}'.format(code=a[0], name=)
# print(
#
# )

if __name__ == '__main__':
    main()