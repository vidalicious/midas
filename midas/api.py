# -*- coding: utf-8 -*-
from functools import reduce

from numpy import mean


def past_hist_p_change(hist_data, past_day=5):
    past_p_changes = hist_data['p_change'][:past_day]
    mul = reduce(lambda x, y: x*y, map(lambda x: 1+x/100, past_p_changes.values))
    return round((mul - 1) * 100, 3)


def past_average_turnover(hist_data, past_day=5):
    turnovers = hist_data['turnover'][:past_day]
    return round(mean(turnovers), 3)
