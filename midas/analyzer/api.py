# -*- coding: utf-8 -*-
import numpy as np


def daily_close_ma(daily=None, step=5):
    if len(daily) < step:
        raise Exception('invalid daily data')

    closes = list()
    for item in daily:
        closes.append(item.close)

    result = list()
    for i in range(len(daily) - step + 1):
        ma = round(np.mean(closes[i:i + step]), 2)
        result.append(ma)

    return result


def daily_weight_eigen_slope(daily=None, begin=0, end=1):
    if begin == end:
        return 0

    weights = list()
    for item in daily[begin:end]:
        weights.append(round((item.high + item.low) / 2, 2))

    min_weight = min(weights)
    min_index = weights.index(min_weight) + begin
    max_weight = max(weights)
    max_index = weights.index(max_weight) + begin
    slope = round((max_weight / min_weight - 1) * 100 / -(max_index - min_index), 2)
    return slope


def daily_weight_rise_efficiency(daily=None, begin=0, end=1):
    if begin == end:
        return (0, begin, begin)

    weights = list()
    for item in daily[begin:end]:
        weights.append(round((item.high + item.low) / 2, 2))

    min_weight = min(weights)
    min_index = weights.index(min_weight) + begin

    if begin == min_index:
        return (0, begin, begin)

    weights = weights[begin:min_index]
    max_weight = max(weights)
    max_index = weights.index(max_weight) + begin
    average_weight_rise = round((max_weight / min_weight - 1) * 100 / -(max_index - min_index), 2)
    return (average_weight_rise, min_index, max_index)


def daily_continuous_limit_count(daily=None):
    for i, item in enumerate(daily):
        if item.pct_chg < 9.9:
            break
    return i


def daily_weight_exponential_fitness(daily=None, begin=0, end=1, exp=2):
    if begin == end:
        return 0

    benchmark = list()
    for i in range(end - begin):
        benchmark.append(round(pow(1 + exp / 100, i), 2))

    weights = list()
    for item in daily[begin:end]:
        weights.append(round((item.high + item.low) / 2, 2))

    weights.reverse()
    # Normalization
    denominator = weights[0]
    weights = list(map(lambda x: x / denominator, weights))
    diff = 0
    for i in range(len(benchmark)):
        diff = diff + pow(weights[i] - benchmark[i], 2)
    score = round(1 / diff, 2)
    return score


def daily_weight_max_chg_gap(daily=None, begin=0, end=1):
    if begin == end:
        return 0

    weights = list()
    for item in daily[begin:end]:
        weights.append(round((item.high + item.low) / 2, 2))

    min_weight = min(weights)
    min_index = weights.index(min_weight) + begin
    max_weight = max(weights)
    max_index = weights.index(max_weight) + begin
    chg = round((max_weight / min_weight - 1) * 100, 2)
    if max_index < min_index:
        result = chg
    else:
        result = -chg
    return result


def daily_minus_combo_count(daily=None):
    for i, item in enumerate(daily):
        if item.open < item.close or item.low == item.high:
            break

    result = i
    return result


def differ(sequence=None):
    res = []
    for i in range(len(sequence) - 1):
        res.append((sequence[i] / sequence[i + 1] - 1) * 100)
    return res


def continuous_positive_count(sequence=None):
    for i, item in enumerate(sequence):
        if item < 0:
            return i
    return i


def avg_vibration_chg(sequence=None):
    total_vibration = 0
    for i, item in enumerate(sequence):
        # high = max(item.high, item.pre_close)
        # low = min(item.low, item.pre_close)
        high_chg = item.high / item.pre_close
        low_chg = item.low / item.pre_close
        vibration = high_chg - low_chg
        total_vibration += vibration

    return total_vibration / (i + 1) * 100


def aggressive_chg_accumulation(sequence=None):
    res = 0
    for i, item in enumerate(sequence):
        if item.pct_chg > 5:
            res += item.pct_chg

    return res


def negative_chg_accumulation(sequence=None):
    res = 0
    for i, item in enumerate(sequence):
        if item.pct_chg < 0:
            res += item.pct_chg

    return res
