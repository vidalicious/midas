# -*- coding: utf-8 -*-
import time

import tushare as ts
import ahocorasick

import midas.core.data.models as models
from midas.core.data.engine import main_session
from midas.core.data.engine import update_to_db




pro = ts.pro_api()
trade_dates = pro.daily(ts_code='000001.SZ').trade_date
LAST_MARKET_DATE = trade_dates[0]


@update_to_db(main_session)
def async_stock_basic():
    main_session.query(models.StockBasicPro).delete()
    main_session.commit()
    stock_basic = pro.stock_basic(list_status='L', fields='ts_code,symbol,name,industry,fullname')
    for i in range(len(stock_basic)):
        a_stock_basic = models.StockBasicPro(ts_code=stock_basic.loc[i, 'ts_code'],
                                             symbol=stock_basic.loc[i, 'symbol'],
                                             name=stock_basic.loc[i, 'name'],
                                             industry=stock_basic.loc[i, 'industry']
                                             )
        main_session.add(a_stock_basic)

    main_session.commit()
    print('##### async stock basic finished #####')


def build_actree(word_list):
    actree = ahocorasick.Automaton()
    for index, word in enumerate(word_list):
        actree.add_word(word, (index, word))
    actree.make_automaton()
    return actree


@update_to_db(main_session)
def async_float_holders():
    main_session.query(models.FloatHolderPro).delete()
    main_session.commit()

    key_words = ['基金', '资产管理', '中央', '信托']
    region_tree = build_actree(key_words)

    for count, sbp in enumerate(main_session.query(models.StockBasicPro).all()):
        if_pass = False
        while not if_pass:
            try:
                float_holders = pro.top10_floatholders(ts_code=sbp.ts_code, start_date=trade_dates[100], end_date=LAST_MARKET_DATE)
                if_pass = True
            except Exception as e:
                print('excetion in {}'.format(count))
                continue

        for i in range(len(float_holders)):
            matches = list(region_tree.iter(float_holders.loc[i, 'holder_name']))
            if matches:
                a_float_holder = models.FloatHolderPro(
                    ts_code=float_holders.loc[i, 'ts_code'],
                    ann_date=float_holders.loc[i, 'ann_date'],
                    holder_name=float_holders.loc[i, 'holder_name']
                )
                main_session.add(a_float_holder)
        main_session.commit()
        print('##### async_float_holders {i} #####'.format(i=count))
        time.sleep(0.2)


if __name__ == '__main__':
    async_float_holders()