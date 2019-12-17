# -*- coding: utf-8 -*-

import midas.core.data.async_base as base
import midas.core.data.async_weekly as weekly
import midas.core.data.async_float_holders as holders
import midas.core.analyzer._0x21Weekly_diffuse as diffuse


def main():
    base.async_stock_basic()
    weekly.async_weekly()
    holders.async_float_holders()
    diffuse.main()


if __name__ == '__main__':
    main()