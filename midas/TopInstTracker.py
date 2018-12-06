# -*- coding: utf-8 -*-
import tushare as ts

pro = ts.pro_api()

# 上证指数
LAST_MARKET_DATE = ts.get_hist_data('000001').index[0]

indice = ts.get_hist_data('000001').index

for i in range(10):
    date = ts.get_hist_data('000001').index[i]


# LAST_MARKET_DATE.replace('-', '')
    df = pro.top_inst(trade_date=date.replace('-', ''))

    df_a = df.loc[:, ['trade_date', 'ts_code', 'buy', 'sell', 'net_buy']]
    df_b = df_a.groupby('ts_code').sum().round(2)
    print('###### {i} ######'.format(i=i))

    file_name = '../logs/{date}@TopInstTracker.csv'.format(date=date)
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        df_b.to_csv(file)
        file.writelines('\n\n')
        df.to_csv(file)
