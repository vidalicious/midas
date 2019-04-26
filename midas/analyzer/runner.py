# -*- coding: utf-8 -*-
import midas.midas.analyzer._0x1Regression as reg
import midas.midas.analyzer._0x2Regression_exp1 as reg1
import midas.midas.analyzer._0x5BrokenPlane as broken
import midas.midas.analyzer._0x4RiseTempo as tempo
import midas.midas.analyzer._0x10Close_ma_dive as closema

if __name__ == '__main__':
    reg.main()
    reg1.main()
    closema.main(10)
    closema.main(20)
    broken.main()
    tempo.main()
