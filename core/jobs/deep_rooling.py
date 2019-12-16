# -*- coding: utf-8 -*-

import midas.core.data.async_base as base
import midas.core.data.async_weekly as weekly
import midas.core.analyzer._0x21Weekly_diffuse as diffuse


def main():
    base.main()
    weekly.main()
    diffuse.main()