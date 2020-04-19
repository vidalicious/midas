# -*- coding: utf-8 -*-

import midas.core.data.async_base as base
import midas.core.data.async_weekly as weekly
import midas.core.data.async_float_holders as holders
import midas.core.analyzer._0x22DemonHunter as demon
import midas.core.analyzer._0x24Drager_List as drager


def working_day():
    base.async_stock_basic()
    base.async_daily()
    demon.main()
    drager.main()


def weekend():
    weekly.async_weekly()
    holders.async_float_holders()
    demon.main()
    drager.main()


def total():
    base.async_stock_basic()
    base.async_daily()
    weekly.async_weekly()
    holders.async_float_holders()
    demon.main()
    drager.main()


if __name__ == '__main__':
    # working_day()
    # weekend()
    total()