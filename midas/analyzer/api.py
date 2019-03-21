# -*- coding: utf-8 -*-


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
