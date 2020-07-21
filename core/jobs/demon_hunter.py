# -*- coding: utf-8 -*-

import midas.core.data.async_base as base
import midas.core.data.async_weekly as weekly
import midas.core.data.async_float_holders as holders
import midas.core.analyzer._0x22DemonHunter as demon_hunter
import midas.core.analyzer._0x26WindChime as wind_chime
import midas.core.analyzer._0x25TwoPlus as two_plus
import midas.core.analyzer._0x24Drager_List as drager
import midas.core.analyzer._0x27Tidal as tidal
import midas.core.analyzer._0x28Local_Break as local_break
import midas.core.analyzer._0x29Medical_Break as medical_break
import midas.core.analyzer._0x34Drink_Break as drink_break
# import midas.core.analyzer._0x32Medical_Ergodic as medical_ergodic
import midas.core.analyzer._0x35Limit_Break as limit_break
import midas.core.analyzer._0x36Aggressive_Break as aggressive_break
import midas.core.analyzer._0x37Medical_Aggressive as medical_aggressive
import midas.core.analyzer._0x40Live_Oneplus as one_plus
import midas.core.analyzer._0x41Ambush as ambush


def working_day():
    base.async_stock_basic()
    base.async_daily()
    base.async_daily_basic_origin()
    ambush.main()
    one_plus.main()
    medical_aggressive.main()
    aggressive_break.main()
    wind_chime.main()
    demon_hunter.main()
    # drager.main()


def total():
    base.async_stock_basic()
    base.async_daily()
    base.async_daily_basic()
    weekly.async_weekly()
    holders.async_float_holders()
    ambush.main()
    one_plus.main()
    medical_aggressive.main()
    aggressive_break.main()
    wind_chime.main()
    demon_hunter.main()
    # drager.main()


if __name__ == '__main__':
    working_day()
    # weekend()
    # total()