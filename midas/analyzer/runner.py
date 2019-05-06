# -*- coding: utf-8 -*-
import midas.midas.analyzer._0x1Regression as reg
import midas.midas.analyzer._0x2Regression_exp1 as reg1
import midas.midas.analyzer._0x5BrokenPlane as broken
import midas.midas.analyzer._0x4RiseTempo as tempo
import midas.midas.analyzer._0x10Close_ma_dive as closema
import midas.midas.analyzer._0x11MA_walker as walker
import midas.midas.analyzer._0x12MA_10_20 as ma1020
import midas.midas.analyzer._0x16DailyLimitLowPrice as dllp

if __name__ == '__main__':
    reg.main()
    reg1.main()
    ma1020.main()
    dllp.main()
