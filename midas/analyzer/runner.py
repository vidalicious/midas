# -*- coding: utf-8 -*-
import midas.midas.analyzer._0x1Regression as reg
import midas.midas.analyzer._0x2Regression_exp1 as reg1
import midas.midas.analyzer._0x12MA_10_20 as ma1020
import midas.midas.analyzer._0x16DailyLimitLowPrice as dllp
import midas.midas.analyzer._0x17MA_diffuse as diffuse
import midas.midas.analyzer._0x18Atmosphere as atmosphere
import midas.midas.analyzer._0x19ContinuousLimit as continuous

if __name__ == '__main__':
    reg.main()
    reg1.main()
    ma1020.main()
    dllp.main()
    diffuse.main()
    atmosphere.main()
    continuous.main()
