# -*- coding: utf-8 -*-

import midas.core.data.async_base as base
import midas.core.data.async_weekly as weekly
import midas.core.data.async_float_holders as holders
import midas.core.analyzer._0x22DemonHunter as demon_hunter
import midas.core.analyzer._0x26WindChime as wind_chime
import midas.core.analyzer._0x25TwoPlus as two_plus
import midas.core.analyzer._0x24Drager_List as drager
import midas.core.analyzer._0x27Tidal as tidal


def working_day():
    base.async_stock_basic()
    base.async_daily()
    demon_hunter.main()
    tidal.main()
    wind_chime.main()
    two_plus.main()
    drager.main()


def weekend():
    weekly.async_weekly()
    holders.async_float_holders()
    demon_hunter.main()
    tidal.main()
    wind_chime.main()
    two_plus.main()
    drager.main()


def total():
    base.async_stock_basic()
    base.async_daily()
    weekly.async_weekly()
    holders.async_float_holders()
    demon_hunter.main()
    tidal.main()
    wind_chime.main()
    two_plus.main()
    drager.main()


if __name__ == '__main__':
    # working_day()
    # weekend()
    total()