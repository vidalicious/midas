# -*- coding: utf-8 -*-
import sys
import os

live_path = os.path.dirname(os.path.realpath(__file__))
core_path = os.path.split(live_path)[0]
root_path = os.path.split(core_path)[0]
parent_path = os.path.split(root_path)[0]
sys.path.append(parent_path)

import threading
from tkinter import *
import tkinter.font as tkFont
import time
import grequests
import pandas as pd
import midas.bin.env as env
from midas.core.data.engine import main_session
import midas.core.data.models as models

target_symbols = [
    '603300',
    '603026',
    '600619',
    '603733'
]
target_symbols = list(set(target_symbols))

class Console():
    def __init__(self):
        self.init_market()
        self.root = Tk()
        self.root.title('Remora')
        a = tkFont.families()
        self.lbl = Label(self.root, justify=LEFT, text="", font=tkFont.Font(family="Helvetica", size=16))
        self.display_msg = ''
        self.updateGUI()

    def init_market(self):
        symbol2code = {}
        self.stock_map = {}
        for stock in main_session.query(models.DailyBasic).all():
            ts_code = stock.ts_code
            market = ts_code.split('.')[1].lower()
            symbol = ts_code.split('.')[0]
            code = '{market}{symbol}'.format(market=market, symbol=symbol)
            symbol2code[symbol] = code
            self.stock_map[code] = {
                'circ_mv': float(stock.circ_mv)
            }

        batch_size = 500
        self.req_list = []
        for i in range(0, len(target_symbols), batch_size):
            keys = []
            for symbol in target_symbols[i:i + batch_size]:
                query_key = symbol2code[symbol]
                keys.append(query_key)

            self.req_list.append(grequests.get('http://hq.sinajs.cn/list={}'.format(','.join(keys))))

    def update_market(self):
        responses = grequests.map(self.req_list)
        # print('====== {} ======'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        displays = []
        for response in responses:
            res = response.text.strip().split(';\n')
            for i in res:
                j = i.split(',')
                name = j[0].split('="')[1]
                code = j[0].split('="')[0].split('_')[-1]
                yesterday_closing_price = float(j[2])
                current_price = float(j[3])

                chg = (current_price / yesterday_closing_price - 1)
                chg_display = '{}%'.format(round(chg * 100, 2))
                circ_mv = self.stock_map[code]['circ_mv']

                displays.append({
                    'note': '{code} {name} chg:{chg} price:{price} circ_mv:{circ_mv}亿'.format(code=code, name=name, chg=chg_display,
                                                                                                  price=round(current_price, 2), circ_mv=int(circ_mv)),
                    'chg': chg
                })

        displays.sort(key=lambda x: x['chg'], reverse=True)
        notes = [i['note'] for i in displays]
        self.display_msg = '====== {} ======\n'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        self.display_msg += '\n'.join(notes)

    def run(self):
        self.lbl.pack()
        self.lbl.after(1000, self.updateGUI)
        self.root.mainloop()

    def updateGUI(self):
        time_a = time.time()
        self.update_market()
        self.lbl["text"] = self.display_msg
        self.root.update()
        time_b = time.time()
        cost = time_b - time_a
        self.lbl.after(1000 - int(cost * 1000), self.updateGUI)


if __name__ == "__main__":
    Console().run()