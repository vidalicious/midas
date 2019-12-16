# -*- coding: utf-8 -*-

import os
import sys

bin_path = os.path.dirname(os.path.realpath(__file__))
root_path = os.path.split(bin_path)[0]
tmp_path = os.path.join(root_path, 'tmp')

sys.path.append(root_path)
sys.path.append(bin_path)
sys.path.append(tmp_path)