# -*- coding: utf-8 -*-
import json
import time
import math
import tushare as ts
import talib
from pandas import DataFrame
import numpy as np
import math
import matplotlib.pyplot as plt
import pandas as pd
import midas.core.analyzer.api as api
import seaborn as sns

import midas.core.data.models as models
from midas.core.data.engine import main_session
import mpl_finance as mpf



def main(offset=0):
    daily001 = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == '000001.SZ').order_by(models.DailyPro.trade_date.desc()).all()
    LAST_MARKET_DATE = daily001[offset].trade_date
    FIRST_MARKET_DATE = daily001[offset + 140].trade_date

    pro = ts.pro_api()
    res = pro.moneyflow_hsgt(start_date=FIRST_MARKET_DATE, end_date=LAST_MARKET_DATE)

    df = DataFrame()
    for i in range(len(res))[::-1]:
        df.loc[i, 'trade_date'] = res.loc[i, 'trade_date']
        df.loc[i, 'north_money'] = res.loc[i, 'north_money']
        df.loc[i, 'open'] = 0.5
        df.loc[i, 'close'] = 1 if res.loc[i, 'north_money'] > 0 else 0.1

    fig = plt.figure(figsize=(17, 10))
    ax = fig.add_subplot(1, 1, 1)

    ax.set_xticks(range(0, len(df['trade_date']), 20))
    ax.set_xticklabels(df['trade_date'][::20])
    plt.title('north_money')
    mpf.volume_overlay(ax, df['open'], df['close'], df['north_money'], colorup='r', colordown='g', width=0.5, alpha=0.8)

    plt.savefig('../../buffer/north_money/{date}_north_money.png'.format(date=LAST_MARKET_DATE))

    pass


if __name__ == '__main__':
    main(offset=0)