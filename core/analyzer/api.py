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
    count = 0
    break_change = 1
    for i, item in enumerate(daily):
        boards = int(item.pct_chg / 9.8)
        if boards > 0:
            count += boards
            break_change = 1
        else:
            break_change -= 1

        if break_change < 0:
            break

    return count


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


def continuous_positive_chg_count(sequence=None):
    if not sequence:
        return 0

    for i, item in enumerate(sequence):
        if item.pct_chg < 0:
            return i
    return len(sequence)


def continuous_positive_average_chg(sequence=None):
    if not sequence:
        return 0

    chg = 0
    for i, item in enumerate(sequence):
        if item.pct_chg < 0:
            if i == 0:
                return 0
            else:
                return chg / i
        chg += item.pct_chg
    return chg / len(sequence)


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


def limit_chg_count(sequence=None):
    res = 0
    for i, item in enumerate(sequence):
        if item.pct_chg > 9.8:
            res += 1

    return res


def crimson_rate(sequence=None):
    crimson = 0
    for i, item in enumerate(sequence):
        if item.close > item.open:
            crimson += 1
    return crimson / len(sequence)


def pct_chg_std(sequence=None):
    chgs = [i.pct_chg for i in sequence]
    std = np.std(chgs)
    return std


def weekly_break(sequence=None):
    weekly_closes = [i.close for i in sequence]
    index = weekly_closes.index(max(weekly_closes))
    return index == 0 and sequence[0].pct_chg > 0.1


def daily_break(sequence=None, local_scale=120):
    sequence = sequence[:local_scale]
    daily_closes = [i.close for i in sequence]
    index = daily_closes.index(max(daily_closes))
    return index < 3


def daily_break_index(sequence=None, local_scale=120):
    sequence = sequence[:local_scale]
    daily_closes = [i.close for i in sequence]
    index = daily_closes.index(max(daily_closes))
    return index


def min_max_gap(sequence=None, local_scale=120):
    sequence = sequence[:local_scale]
    daily_closes = [i.close for i in sequence]
    max_close = max(daily_closes)
    min_close = min(daily_closes)
    gap = max_close / min_close - 1
    return gap * 100


def daily_pit(sequence=None, local_scale=20):
    sequence = sequence[:local_scale]
    daily_closes = [i.close for i in sequence]
    index = daily_closes.index(min(daily_closes))
    return 2 < index < 10


def no_limit(sequence=None):
    for i, item in enumerate(sequence):
        if item.pct_chg > 9.8:
            return False
    return True


def is_medical(message):
    for key in ['医', '药', '健康', '基因', '生物']:
        if key in message and '农药' not in message:
            return True
    return False


def is_drink(message):
    for key in ['白酒', '红黄酒']:
        if key in message:
            return True
    return False


def amplitude(sequence=None):
    closes = [i.close for i in sequence]
    amplitude = (max(closes) / min(closes) - 1) * 100
    return amplitude


def recent_limit(sequence=None):
    chgs = [i.pct_chg for i in sequence]
    for i in range(3):
        if chgs[i] > 9:
            return True
    return False


def recent_aggressive(sequence=None):
    chgs = [i.pct_chg for i in sequence]
    for i in range(3):
        if chgs[i] > 5:
            return True
    return False


def daily_local_max(sequence=None, local_scale=120):
    sequence = sequence[:local_scale]
    closes = [i.close for i in sequence]
    return max(closes)


def daily_local_min(sequence=None, local_scale=120):
    sequence = sequence[:local_scale]
    closes = [i.close for i in sequence]
    return min(closes)


def average_abs_chg(sequence=None, local_scale=120):
    sequence = sequence[:local_scale]
    chgs = [abs(i.pct_chg) for i in sequence]
    mean = np.mean(chgs)
    return mean


def daily_silent(sequence=None, local_scale=5):
    sequence = sequence[:local_scale]
    chgs = [i.pct_chg for i in sequence]
    for i in chgs:
        if i > 9.8:
            return False
    return True


def local_limit_count(sequence=None, local_scale=5):
    sequence = sequence[:local_scale]
    chgs = [i.pct_chg for i in sequence]
    limit_count = 0
    for i in chgs:
        if i > 9.8:
            limit_count += 1
    return limit_count


def klines_max_retracement(sequence=None):
    if not sequence:
        return 0

    max_retracement = 0
    for item in sequence:
        entity_max = max(item.open, item.close)
        entity_min = min(item.open, item.close)
        total_max = max(item.high, item.low)
        total_min = min(item.high, item.low)

        retracement_up = abs(entity_max / total_max  - 1)
        retracement_bottom = abs(total_min / entity_min - 1)

        max_retracement = max(max_retracement, retracement_up, retracement_bottom)

    return max_retracement


def klines_comfort_score(sequence=None):
    if not sequence:
        return 0

    comfort_score = 0
    count = 0
    for item in sequence:
        entity_max = max(item.open, item.close)
        entity_min = min(item.open, item.close)
        total_max = max(item.high, item.low)
        total_min = min(item.high, item.low)

        retracement_up = abs(entity_max / total_max  - 1)
        retracement_bottom = abs(total_min / entity_min - 1)

        pct_chg = item.close / item.pre_close - 1

        score = (pct_chg - retracement_up - retracement_bottom) * 100
        # if score < 0:
        #     break

        comfort_score += score
        count += 1

    if count == 0:
        return 0
    else:
        return comfort_score / count
