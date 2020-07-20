# -*- coding: utf-8 -*-

import os
import sys

bin_path = os.path.dirname(os.path.realpath(__file__))
root_path = os.path.split(bin_path)[0]
tmp_path = os.path.join(root_path, 'tmp')
logs_path = os.path.join(root_path, 'logs')
live_logs_path = os.path.join(root_path, 'live_logs')
data_path = os.path.join(root_path, 'data')
buffer_path = os.path.join(root_path, 'buffer')

sys.path.append(root_path)
sys.path.append(bin_path)
sys.path.append(tmp_path)