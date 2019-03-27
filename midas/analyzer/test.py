# -*- coding: utf-8 -*-
import json
import time

import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.midas.analyzer.api as api

import midas.midas.data.models as models
from midas.midas.data.engine import main_session
import midas.midas.analyzer._0x3MinusCombo as combo

df0 = combo.main(0)
df1 = combo.main(1)

l = list()
for i, item0 in df0.iterrows():
    for j, item1 in df1.iterrows():
        if item0.ts_code == item1.ts_code:
            l.append('{code} {name}'.format(code=item0.ts_code, name=item0.name))

print(l)