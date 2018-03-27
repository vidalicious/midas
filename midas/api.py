# -*- coding: utf-8 -*-
from functools import reduce

import numpy as np


def past_hist_p_change(hist_data, past_day=5):
    # past_p_changes = hist_data['p_change'][:past_day]
    # mul = reduce(lambda x, y: x*y, map(lambda x: 1+x/100, past_p_changes.values))
    # return round((mul - 1) * 100, 3)
    return hist_p_change(hist_data, begin=0, end=past_day)


def hist_p_change(hist_data, begin=0, end=5):
    p_changes = hist_data['p_change'][begin:end]
    mul = reduce(lambda x, y: x*y, map(lambda x: 1+x/100, p_changes))
    return round((mul - 1) * 100, 3)


def past_average_turnover(hist_data, past_day=5):
    turnovers = hist_data['turnover'][:past_day]
    return round(np.mean(turnovers), 3)


def is_cross_ma5_ma10(hist_data):
    ma5_0 = hist_data['ma5'][0]
    ma10_0 = hist_data['ma10'][0]
    ma5_1 = hist_data['ma5'][1]
    ma10_1 = hist_data['ma10'][1]
    return ma5_0 > ma10_0 and ma5_1 < ma10_1


def normalizing_std_close(hist_data, begin=0, end=5):
    closes = hist_data['close'][begin:end]
    mean = np.mean(closes)
    std = np.std(closes)
    return round(std / mean, 3)
