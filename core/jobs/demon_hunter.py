# -*- coding: utf-8 -*-

import midas.core.data.async_base as base
import midas.core.data.async_monthly as monthly
import midas.core.data.async_float_holders as holders
import midas.core.analyzer._0x43North_Money as north_money
import midas.core.analyzer._0x45Limit_Rank as limit_rank
import midas.core.analyzer._0x46Wind_Chime_V2 as wind_chime
import midas.core.analyzer._0x62Concept_Rank as concept_rank
import midas.core.analyzer._0x64Whole_Rank as whole_rank
import midas.core.analyzer._0x65Past_Intensity as past_intensity


def working_day():
    base.async_stock_basic()
    base.async_daily()
    base.async_daily_basic_origin()
    north_money.main()
    past_intensity.main()
    # concept_rank.main()
    whole_rank.main()
    limit_rank.main()
    wind_chime.main()


def total():
    base.async_stock_basic()
    base.async_daily()
    base.async_daily_basic_origin()
    monthly.async_monthly()
    holders.async_float_holders()
    north_money.main()
    past_intensity.main()
    # concept_rank.main()
    whole_rank.main()
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