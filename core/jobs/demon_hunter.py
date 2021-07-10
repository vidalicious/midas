# -*- coding: utf-8 -*-

import midas.core.data.async_base as base
import midas.core.data.async_monthly as monthly
import midas.core.data.async_float_holders as holders
import midas.core.analyzer._0x43North_Money as north_money
import midas.core.analyzer._0x45Limit_Rank as limit_rank
import midas.core.analyzer._0x46Wind_Chime_V2 as wind_chime
import midas.core.analyzer._0x70_Window_Probability as window_probability
import midas.core.analyzer._0x71_Window_Aggressive as window_aggressive


def working_day():
    base.async_stock_basic()
    base.async_daily()
    base.async_daily_basic_origin()
    north_money.main()
    window_aggressive.main()
    # window_probability.main()
    # window_probability_st.main()
    limit_rank.main()
    wind_chime.main()


def total():
    base.async_stock_basic()
    base.async_daily()
    base.async_daily_basic_origin()
    monthly.async_monthly()
    holders.async_float_holders()
    north_money.main()
    window_aggressive.main()
    # window_probability.main()
    # window_probability_st.main()
    limit_rank.main()
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