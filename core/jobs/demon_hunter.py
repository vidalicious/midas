# -*- coding: utf-8 -*-

import midas.core.data.async_base as base
import midas.core.data.async_float_holders as holders
import midas.core.analyzer._0x22DemonHunter as demon


def working_day():
    base.async_stock_basic()
    base.async_daily()
    demon.main()


def weekend():
    holders.async_float_holders()
    demon.main()


def total():
    base.async_stock_basic()
    base.async_daily()
    holders.async_float_holders()
    demon.main()


if __name__ == '__main__':
    working_day()
    # weekend()
    # total()