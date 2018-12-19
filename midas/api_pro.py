# -*- coding: utf-8 -*-
import numpy as np
from functools import reduce
# 华泰证券深圳荣超商务中心


def daily_continuously_low_up_count(daily=None):
    lows = daily.low
    for i in range(len(lows)):
        if lows[i] < lows[i + 1]:
            return i
    return len(lows)


def daily_break_continuously_high_fall_count(daily=None):
    highs = daily.high
    if highs[0] < highs[2]:
        return 0
    for i in range(1, len(highs)):
        if highs[i] > highs[i + 1]:
            return i - 1    # offset
    return len(highs)


def daily_average_p_change(daily=None, begin=0, end=1):
    if begin == end:
        return 0
    p_changes = daily.pct_chg
    result = round(np.mean(p_changes[begin:end]), 3)
    return result


def daily_accumulate_p_change(daily=None, begin=0, end=1):
    if begin == end:
        return 0
    p_changes = daily.pct_chg
    mul = reduce(lambda x, y: x * y, map(lambda x: 1 + x / 100, p_changes[begin:end]))
    result = round((mul - 1) * 100, 3)
    return result


def daily_highest_close(daily=None, begin=0, end=1):
    closes = daily.close[begin:end]
    result = closes.max()
    return result


def daily_max_jump_p_change(daily=None, begin=0, end=1):
    highest_close = daily_highest_close(daily=daily, begin=begin, end=end)
    last_close = daily.close[0]
    result = round((last_close / highest_close) - 1, 3)
    return result


def daily_inday_p_change(daily=None, index=0):
    close = daily.close[0]
    open = daily.open[0]
    result = round((close / open) - 1, 3)
    return result


def daily_basic_average_turnover_rate(daily_basic=None, begin=0, end=1):
    turnover_rates = daily_basic.turnover_rate
    result = round(np.mean(turnover_rates[begin:end]), 3)
    return result
