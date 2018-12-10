import tushare as ts
from pandas import DataFrame
import numpy as np

COL_TURNOVER = 'turnover'

sampling_count = 100


def main():
    pro = ts.pro_api()

    trade_dates = pro.daily(ts_code='000001.SZ').trade_date
    LAST_MARKET_DATE = trade_dates[0]

    stock_basic = pro.stock_basic(list_status='L', fields='ts_code,symbol,name,industry,fullname')

    data_frame = DataFrame()
    for key in ['ts_code', 'name', 'industry']:
        data_frame[key] = stock_basic[key]

    data_frame[COL_TURNOVER] = np.nan

    for i, ts_code in enumerate(data_frame.ts_code):
        try:
            daily_basic = pro.daily_basic(ts_code=ts_code,
                                          trade_date=LAST_MARKET_DATE)  # start_date=trade_dates[sampling_count], end_date=LAST_MARKET_DATE)
            data_frame.loc[i, COL_TURNOVER] = daily_basic.loc[0, 'turnover_rate']
        except Exception as e:
            print('excetion in {}'.format(i))
            continue
        print('##### {i} #####'.format(i=i))

    sorted_frame = data_frame.sort_values(by=COL_TURNOVER, ascending=False)

    file_name = '../logs/{date}@TestPro.csv'.format(date=LAST_MARKET_DATE)
    # print(fileName)
    with open(file_name, 'w', encoding='utf8') as file:
        sorted_frame.to_csv(file)


if __name__ == '__main__':
    main()