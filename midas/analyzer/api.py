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
