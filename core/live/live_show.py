# -*- coding: utf-8 -*-
import requests
import time
import datetime
import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.core.analyzer.api as api

import midas.core.data.models as models
from midas.core.data.engine import main_session

# 这个字符串由许多数据拼接在一起，不同含义的数据用逗号隔开了，按照程序员的思路，顺序号从0开始。
# 0：”大秦铁路”，股票名字；
# 1：”27.55″，今日开盘价；
# 2：”27.25″，昨日收盘价；
# 3：”26.91″，当前价格；
# 4：”27.55″，今日最高价；
# 5：”26.20″，今日最低价；
# 6：”26.91″，竞买价，即“买一”报价；
# 7：”26.92″，竞卖价，即“卖一”报价；
# 8：”22114263″，成交的股票数，由于股票交易以一百股为基本单位，所以在使用时，通常把该值除以一百；
# 9：”589824680″，成交金额，单位为“元”，为了一目了然，通常以“万元”为成交金额的单位，所以通常把该值除以一万；
# 10：”4695″，“买一”申请4695股，即47手；
# 11：”26.91″，“买一”报价；
# 12：”57590″，“买二”
# 13：”26.90″，“买二”
# 14：”14700″，“买三”
# 15：”26.89″，“买三”
# 16：”14300″，“买四”
# 17：”26.88″，“买四”
# 18：”15100″，“买五”
# 19：”26.87″，“买五”
# 20：”3100″，“卖一”申报3100股，即31手；
# 21：”26.92″，“卖一”报价
# (22, 23), (24, 25), (26,27), (28, 29)分别为“卖二”至“卖四的情况”
# 30：”2008-01-11″，日期；
# 31：”15:05:32″，时间；

sampling_count = 40


def main():
    date = time.strftime("%Y-%m-%d", time.localtime())
    f = open('../../logs/{date}@liveshow.txt'.format(date=date), 'a', encoding='utf8')
    # f_note = open('../../logs/{date}@liveshow_note.txt'.format(date=date), 'a', encoding='utf8')
    daily001 = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == '000001.SZ').order_by(models.DailyPro.trade_date.desc()).all()
    LAST_MARKET_DATE = daily001[0].trade_date

    while int(time.strftime("%H%M%S", time.localtime())) < 92500:
        print('sleep for 5 secs, {}'.format(time.strftime("%H:%M:%S", time.localtime())))
        time.sleep(5)

    while int(time.strftime("%H%M%S", time.localtime())) < 93000:
        for i, stock_basic in enumerate(main_session.query(models.StockBasicPro).all()):
            try:
                query_key = '{a}{b}'.format(a=stock_basic.ts_code.split('.')[1].lower(), b=stock_basic.symbol)
                response = requests.get('http://hq.sinajs.cn/list={}'.format(query_key))
                res = response.text.split(',')
                chg = round((float(res[3]) / float(res[2]) - 1) * 100, 2)

                # f.write(formatted)
                print(i)

                if chg > 4 and float(res[9]) > 50000000:
                    daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == stock_basic.ts_code,
                                                                       models.DailyPro.trade_date <= LAST_MARKET_DATE).order_by(
                        models.DailyPro.trade_date.desc()).limit(sampling_count).all()

                    continuous_limit = api.daily_continuous_limit_count(daily=daily)

                    cons = main_session.query(models.ConceptPro).join(models.ConceptDetailPro,
                                                                      models.ConceptPro.code == models.ConceptDetailPro.code).filter(
                        models.ConceptDetailPro.ts_code == stock_basic.ts_code).all()
                    concept_value = ''
                    for con in cons:
                        concept_value = concept_value + '{c}, '.format(c=con.name)

                    formatted = '{index} {code} {name} 今开:{open} 昨收:{yesterday} 当前百分比:{chg} 当前:{current} 成交股数:{stocks}手 成交额:{amount}万 {date} ' \
                                '{timestamp} 连板:{conti_limit} 概念:{concept}\n'.format(index=i, code=stock_basic.ts_code, name=stock_basic.name, open=res[1],
                                                                                     yesterday=res[2], chg=chg, current=res[3], stocks=round(float(res[8]) / 100, 0),
                                                                                     amount=round(float(res[9]) / 10000, 2), date=res[30], timestamp=res[31], conti_limit=continuous_limit,
                                                                                     concept=concept_value)

                    f.write(formatted)
                    f.flush()
            except Exception as e:
                print('exception in index:{index} {code} {name}'.format(index=i, code=stock_basic.ts_code,
                                                                       name=stock_basic.name))
                continue

        f.write('\n############################################################################\n\n')
        f.flush()

    while int(time.strftime("%H%M%S", time.localtime())) < 150000:
        for i, stock_basic in enumerate(main_session.query(models.StockBasicPro).all()):
            try:
                query_key = '{a}{b}'.format(a=stock_basic.ts_code.split('.')[1].lower(), b=stock_basic.symbol)
                response = requests.get('http://hq.sinajs.cn/list={}'.format(query_key))
                res = response.text.split(',')
                chg = round((float(res[3]) / float(res[2]) - 1) * 100, 2)
                print(i)

                stock_live = main_session.query(models.StockLive).filter(models.StockLive.ts_code == stock_basic.ts_code).first()
                if stock_live:
                    if chg - stock_live.chg > 2:
                        daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == stock_basic.ts_code,
                                                                           models.DailyPro.trade_date <= LAST_MARKET_DATE).order_by(
                            models.DailyPro.trade_date.desc()).limit(sampling_count).all()

                        continuous_limit = api.daily_continuous_limit_count(daily=daily)

                        cons = main_session.query(models.ConceptPro).join(models.ConceptDetailPro,
                                                                          models.ConceptPro.code == models.ConceptDetailPro.code).filter(
                            models.ConceptDetailPro.ts_code == stock_basic.ts_code).all()
                        concept_value = ''
                        for con in cons:
                            concept_value = concept_value + '{c}, '.format(c=con.name)

                        formatted = '{index} {code} {name} 今开:{open} 昨收:{yesterday} 当前百分比:{chg} 当前:{current} {date} ' \
                                    '{timestamp} 连板:{conti_limit} 概念:{concept}\n'.format(index=i, code=stock_basic.ts_code, name=stock_basic.name, open=res[1],
                                                                                         yesterday=res[2], chg=chg, current=res[3], date=res[30], timestamp=res[31], conti_limit=continuous_limit,
                                                                                         concept=concept_value)
                        print(formatted)
                        f.write(formatted)
                        f.flush()
                    stock_live.chg = chg
                    stock_live.timestamp = datetime.datetime.now()
                else:
                    stock_live = models.StockLive(chg=chg, ts_code=stock_basic.ts_code)
                    main_session.add(stock_live)
            except Exception as e:
                print('exception in index:{index} {code} {name}'.format(index=i, code=stock_basic.ts_code,
                                                                       name=stock_basic.name))
                continue
        main_session.commit()
    f.close()

# value = requests.get('http://hq.sinajs.cn/list=sz000001')
# a = value.text.split(',')
# formatted = '{code} {name} 今开:{open} 昨收:{yesterday} 当前:{current} 成交股数:{stocks} 成交额:{amount} {date} ' \
#             '{timestamp}'.format(code=a[0], name=)
# print(
#
# )


if __name__ == '__main__':
    main()