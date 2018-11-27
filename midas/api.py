# -*- coding: utf-8 -*-
from functools import reduce

import numpy as np


def past_hist_p_change(hist_data, past_day=5):
    # past_p_changes = hist_data['p_change'][:past_day]
    # mul = reduce(lambda x, y: x*y, map(lambda x: 1+x/100, past_p_changes.values))
    # return round((mul - 1) * 100, 3)
    return hist_p_change(hist_data, begin=0, end=past_day)


def hist_p_change(hist_data, begin=0, end=5):
    if begin == end:
        return 0
    p_changes = hist_data['p_change'][begin:end]
    mul = reduce(lambda x, y: x*y, map(lambda x: 1+x/100, p_changes))
    return round((mul - 1) * 100, 3)


def past_average_turnover(hist_data, past_day=5):
    # turnovers = hist_data['turnover'][:past_day]
    # return round(np.mean(turnovers), 3)
    return hist_average_turnover(hist_data, begin=0, end=past_day)


def hist_average_turnover(hist_data, begin=0, end=5):
    turnovers = hist_data['turnover'][begin:end]
    return round(np.mean(turnovers), 3)


def hist_daily_hairy(hist_data, begin=0, end=5):
    highs = hist_data['high'][begin:end]
    lows = hist_data['low'][begin:end]
    hairs = (highs - lows) / lows
    return round(np.mean(hairs), 3)


def is_cross_ma5_ma10(hist_data):
    ma5_0 = hist_data['ma5'][0]
    ma10_0 = hist_data['ma10'][0]
    ma5_1 = hist_data['ma5'][1]
    ma10_1 = hist_data['ma10'][1]
    return ma5_0 > ma10_0 and ma5_1 < ma10_1


def normalizing_std_close(hist_data, begin=0, end=5):
    if begin == end:
        return 0
    closes = hist_data['close'][begin:end]
    mean = np.mean(closes)
    std = np.std(closes)
    return round(std / mean, 3)


def std_close(hist_data, begin=0, end=5):
    closes = hist_data['close'][begin:end]
    std = np.std(closes)
    return round(std, 3)


def last_ma5(hist_data):
    return hist_data['ma5'][0]


def is_cross_ma5(hist_data):
    ma5 = hist_data['ma5'][0]
    open = hist_data['open'][0]
    close = hist_data['close'][0]
    return open < ma5 < close


def next_close_to_ma(hist_data, n=5):
    """
    使接触ma5的close
    (a+b+c+d+e)  / 5 = e ==> e = (a+b+c+d) / 4
    """
    k = n - 1
    res = sum(hist_data['close'][0:k]) / k
    return round(res, 3)


def next_close_to_tunnel_top(hist_data, n=5, ratio=3):
    """
    使接触到通道顶
    e - (a+b+c+d+e)  / 5 = ratio * std ==> e = (5 * ratio * std + (a+b+c+d)) / 4
    """
    closes = hist_data['close'][0:n-1]
    std = np.std(closes)
    res = (n * ratio * std + sum(closes)) / (n - 1)
    return round(res, 3)


def is_COG_continuously_increase(hist_data, begin=0, end=5):
    """重心一直增加"""
    pre_COG = 0
    for i in range(begin, end):
        COG = (hist_data['open'][i] + hist_data['close'][i]) / 2
        if COG < pre_COG:
            return False
        pre_COG = COG

    return True


def is_COG_above_ma5(hist_data, begin=0, end=5):
    """重心都>ma5"""
    for i in range(begin, end):
        COG = (hist_data['open'][i] + hist_data['close'][i]) / 2
        if COG < hist_data['ma5'][i]:
            return False

    return True
