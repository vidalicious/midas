# -*- coding: utf-8 -*-
import numpy as np
from functools import reduce


def daily_continuously_low_up_count(daily=None):
    lows = daily.low
    for i in range(len(lows)):
        if lows[i] < lows[i + 1]:
            return i
    return len(lows)


def daily_average_p_change(daily=None, count=1):
    if count == 0:
        return 0
    p_changes = daily.pct_chg
    result = round(np.mean(p_changes[:count]), 3)
    return result


def daily_accumulate_p_change(daily=None, count=1):
    if count == 0:
        return 0
    p_changes = daily.pct_chg
    mul = reduce(lambda x, y: x * y, map(lambda x: 1 + x / 100, p_changes[:count]))
    result = round((mul - 1) * 100, 3)
    return result
