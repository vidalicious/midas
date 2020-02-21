# -*- coding: utf-8 -*-

import pandas as pd
from pandas import DataFrame
from os import listdir
import midas.core.analyzer.api as api

import midas.core.data.models as models
from midas.core.data.engine import main_session
import midas.bin.env as env


def diff(offset0=0, offset1=1):
    daily001 = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == '000001.SZ').order_by(models.DailyPro.trade_date.desc()).all()
    date_0 = daily001[offset0].trade_date
    date_1 = daily001[offset1].trade_date

    df_0 = pd.read_csv('{logs_dir}/{file}'.format(logs_dir=env.logs_path, file='{date}@demon_hunter.csv'.format(date=date_0)))
    df_1 = pd.read_csv('{logs_dir}/{file}'.format(logs_dir=env.logs_path, file='{date}@demon_hunter.csv'.format(date=date_1)))

    df_0 = df_0.loc[:, ['ts_code', 'name', 'COL_DAILY_AGGRESSIVE_ACCUMULATION']]
    df_0 = df_0[df_0['COL_DAILY_AGGRESSIVE_ACCUMULATION'] > 0]

    df_1 = df_1.loc[:, ['ts_code', 'name', 'COL_DAILY_AGGRESSIVE_ACCUMULATION']]
    df_1 = df_1[df_1['COL_DAILY_AGGRESSIVE_ACCUMULATION'] > 0]

    df_0_list = df_0.values.tolist()
    df_1_list = df_1.values.tolist()
    res = {}
    for item in df_0_list:
        res[item[0]] = item[2]

    power_rookies = []
    for item in df_1_list:
        if item[0] in res and item[2] < res[item[0]]:
            power_rookies.append('{code} {name}'.format(code=item[0], name=item[1]))

    return power_rookies
    pass


def main():
    for i in range(4):
        rookies = diff(offset0=i, offset1=i + 1)
        if i == 0:
            power_rookies = rookies
        else:
            for item in power_rookies:
                if item not in rookies:
                    power_rookies.remove(item)

            if not power_rookies:
                break

    return power_rookies



if __name__ == '__main__':
    a = main()
    pass