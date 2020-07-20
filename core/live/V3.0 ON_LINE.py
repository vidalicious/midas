import pandas
import csv
import numpy
import numpy as np
import pandas as pd
import requests
import csv
import datetime
import warnings
import re
warnings.filterwarnings("ignore")

class v2_data(object):
    def __init__(self):
        self.url = 'http://hq.sinajs.cn/list=%s'

    def round_up(self,value):
        return round(value*100)/100.0

    def getdate(self, beforeOfDay):
        today = datetime.datetime.now()
        # 计算偏移量
        offset = datetime.timedelta(days=-beforeOfDay)
        # 获取想要的日期的时间
        re_date = (today + offset).strftime('%Y-%m-%d')
        return re_date

    def Refresh_the_quotation(self, code_num,data):
        num = int(code_num)
        if num >= 600000:
            num = 'sh' + str(num)
        else:
            num = 'sz' + str(num+1000000)[-6:]
        request_num =num
        url = self.url % request_num
        response = requests.get(url=url, verify=False)
        data_url = response.content.decode('gbk')
        data_url = data_url.split(',')
        data_Dataframe = pandas.DataFrame(
            [[data_url[30],
              data_url[1],
              data_url[4],
              data_url[5],
              data_url[3],
              data_url[8],
              data_url[9]]],
            columns=['date', 'open', 'high', 'low', 'close', 'vol', 'amount'])
        data = data.append(data_Dataframe, ignore_index=False)
        data.reset_index(inplace=True)
        data=data[['open','high', 'low', 'close', 'vol', 'amount']].astype(float)


    def get_stock_pool(self):
        code_data_list = pandas.read_csv('C:\\Users\\47177\\data\\code_list\\code_list.csv', encoding='gbk')
        for num in range(0, len(code_data_list)):
            code_num = code_data_list['ts_code'][num][0:6]
            code_data = pandas.read_csv('C:\\Users\\47177\\data\\tdx_stock_data\\%s.csv' % code_num, encoding='gbk',names=['date', 'open', 'high', 'low', 'close', 'vol', 'amount'])
            code_data.dropna(inplace=True)
            self.Refresh_the_quotation(code_num,code_data)


    def run(self):
        for i in range(1,1000):
            self.get_stock_pool()


if __name__ == '__main__':
    v2_data=v2_data()
    v2_data.run()