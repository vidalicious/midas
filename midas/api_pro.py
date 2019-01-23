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


def daily_continuously_close_up_count(daily=None):
    closes = daily.close
    for i in range(len(closes)):
        if closes[i] < closes[i + 1]:
            return i
    return len(closes)


def daily_continuously_limit_up_count(daily=None):
    p_changes = daily.pct_chg
    for i in range(len(p_changes)):
        if p_changes[i] < 9.8:
            return i
    return len(p_changes)


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
    close = daily.close[index]
    open = daily.open[index]
    result = round((close / open) - 1, 3)
    return result


def daily_ma(daily=None, begin=0, end=1, step=5):
    closes = daily.close[begin:end + step]
    result = list()
    for i in range(begin, end):
        ma = round(np.mean(closes[i:i + step - 1]), 2)
        result.append(ma)

    return result


def daily_weight_continuously_fall_p_change(daily=None, begin=0):
    lows = daily.low
    highs = daily.high

    begin_weight = (lows[begin] + highs[begin]) / 2
    for i in range(begin, len(lows)):
        if lows[i] + highs[i] < lows[i + 1] + highs[i + 1]:
            continue
        end_weight = (lows[i] + highs[i]) / 2
        break

    if not end_weight:
        end_weight = (lows[-1] + highs[-1]) / 2

    result = round(((begin_weight / end_weight) - 1) * 100, 2)
    return result


def daily_weight_p_change(daily=None, begin=0, end=0):
    lows = daily.low
    highs = daily.high

    begin_weight = (lows[begin] + highs[begin]) / 2
    end_weight = (lows[end] + highs[end]) / 2
    result = round(((begin_weight / end_weight) - 1) * 100, 2)
    return result


def daily_period_weight(daily=None, begin=0, end=0):
    lows = daily.low[begin:end]
    highs = daily.high[begin:end]

    low_min = lows.min()
    high_max = highs.max()
    result = round((low_min + high_max) / 2, 2)
    return result


def daily_basic_average_turnover_rate(daily_basic=None, begin=0, end=1):
    turnover_rates = daily_basic.turnover_rate
    result = round(np.mean(turnover_rates[begin:end]), 3)
    return result


def weekly_continuously_low_up_count(weekly=None):
    lows = weekly.low
    for i in range(len(lows)):
        if lows[i] < lows[i + 1]:
            return i
    return len(lows)


def weekly_continuously_weight_up_count(weekly=None):
    lows = weekly.low
    highs = weekly.high
    for i in range(len(lows)):
        if lows[i] + highs[i] < lows[i + 1] + highs[i + 1]:
            return i
    return len(lows)


def weekly_average_p_change(weekly=None, begin=0, end=1):
    if begin == end:
        return 0
    p_changes = weekly.pct_chg
    result = round(np.mean(p_changes[begin:end]), 3)
    return result


def weekly_weight_p_change(weekly=None, begin=0, end=0):
    lows = weekly.low
    highs = weekly.high

    begin_weight = (lows[begin] + highs[begin]) / 2
    end_weight = (lows[end] + highs[end]) / 2
    result = round(((begin_weight / end_weight) - 1) * 100, 2)
    return result