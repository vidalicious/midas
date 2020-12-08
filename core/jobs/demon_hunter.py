# -*- coding: utf-8 -*-

import midas.core.data.async_base as base
import midas.core.data.async_monthly as monthly
import midas.core.data.async_float_holders as holders
import midas.core.analyzer._0x22DemonHunter as demon_hunter
import midas.core.analyzer._0x40Live_Oneplus as one_plus
import midas.core.analyzer._0x41Ambush as ambush
import midas.core.analyzer._0x42Medical_Ambush as medical_ambush
import midas.core.analyzer._0x43North_Money as north_money
import midas.core.analyzer._0x44Today_Limit as today_limit
import midas.core.analyzer._0x45Limit_Rank as limit_rank
import midas.core.analyzer._0x46Wind_Chime_V2 as wind_chime
import midas.core.analyzer._0x49Ergodic_Graph as ergodic_graph
import midas.core.analyzer._0x50Monthly_Trend as monthly_trend


def working_day():
    base.async_stock_basic()
    base.async_daily()
    base.async_daily_basic_origin()
    north_money.main()
    limit_rank.main()
    # ergodic_graph.main()
    wind_chime.main()


def total():
    base.async_stock_basic()
    base.async_daily()
    base.async_daily_basic_origin()
    monthly.async_weekly()
    holders.async_float_holders()
    north_money.main()
    limit_rank.main()
    monthly_trend.main()
    # ergodic_graph.main()
    wind_chime.main()


def gathering():
    base.async_stock_basic()
    base.async_daily()
    base.async_daily_basic_origin()


if __name__ == '__main__':
    # gathering()
    working_day()
    # weekend()
    # total()