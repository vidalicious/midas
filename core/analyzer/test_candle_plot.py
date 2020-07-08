import talib
import numpy as np
import tushare as ts
import matplotlib.pyplot as plt
import mplfinance as mpf
from pandas import DataFrame
from datetime import datetime


data = ts.get_k_data('399300', index=True, start='2017-01-01', end='2017-06-31')
sma_10 = talib.SMA(np.array(data['close']), 10)
sma_30 = talib.SMA(np.array(data['close']), 30)

# fig = plt.figure(figsize=(24, 8))
# ax = fig.add_subplot(1, 1, 1)
# ax.set_xticks(range(0, len(data['date']), 10))
# ax.set_xticklabels(data['date'][::10])
# ax.plot(sma_10, label='10 日均线')
# ax.plot(sma_30, label='30 日均线')
# ax.legend(loc='upper left')

# mpf.plot(ax, data['open'], data['close'], data['high'], data['low'],
#                      width=0.5, colorup='r', colordown='green',
#                      alpha=0.6, type='candle')


df = DataFrame()
for i in range(len(data)):
    # a = datetime.strptime(data.loc[i, 'date'], '%Y-%m-%d')
    date = datetime.strptime(data.loc[i, 'date'], '%Y-%m-%d')
    # df.loc[date, 'Date'] = datetime.strptime(data.loc[i, 'date'], '%Y-%m-%d')
    df.loc[date, 'Open'] = data.loc[i, 'open']
    df.loc[date, 'High'] = data.loc[i, 'high']
    df.loc[date, 'Low'] = data.loc[i, 'low']
    df.loc[date, 'Close'] = data.loc[i, 'close']
    pass

color_sytle = mpf.make_marketcolors(
	up='red',
	down='green',
	# edge='i',
	# wick='i',
	# volume='in',
	inherit=True)
style = mpf.make_mpf_style(
	marketcolors=color_sytle)
# type='candle', type='line', type='renko', or type='pnf'
# data = data.loc[:, ['date', 'open', 'high', 'low', 'close']]
# data.rename(columns={'date':'Date', 'open':'Open', 'high':'High', 'low': 'Low', 'close': 'Close'}, inplace = True)
mpf.plot(df, type='candle', style=style, title='test label')




def plot_candle_gather(data_frame, last_date):
    columns = 5
    rows = math.ceil(len(data_frame) / columns)

    color_sytle = mpf.make_marketcolors(
        up='red',
        down='green',
        edge='i',
        wick='i',
        volume='in',
        inherit=True)
    style = mpf.make_mpf_style(
        marketcolors=color_sytle)

    fig = plt.figure(figsize=(columns * 5, rows * 5 / 2))
    # sns.set(style="whitegrid")
    for i in range(len(data_frame)):
        ts_code = data_frame.loc[i, 'ts_code']
        name = data_frame.loc[i, 'name']
        ax = fig.add_subplot(rows, columns, i + 1)
        # plt.subplot(rows, columns, i + 1)
        # plot_single(ts_code=ts_code, name=name, last_date=last_date, holders_count=data_frame.loc[i, COL_HOLDERS_COUNT])
        plot_candle(ax=ax, ts_code=ts_code, name=name, last_date=last_date, holders_count=data_frame.loc[i, COL_HOLDERS_COUNT], style=style)

    plt.tight_layout()
    plt.savefig('../../buffer/aggressive_break/{date}_aggressive_break.png'.format(date=last_date))

def plot_candle(ax, ts_code, name, last_date, holders_count, style):
    daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == ts_code,
                                                       models.DailyPro.trade_date <= last_date).order_by(
        models.DailyPro.trade_date.desc()).limit(sampling_count).all()

    df = DataFrame()
    for item in daily[:60]:

        date = datetime.strptime(str(item.trade_date), '%Y%m%d')
        df.loc[date, 'Open'] = item.open
        df.loc[date, 'High'] = item.high
        df.loc[date, 'Low'] = item.low
        df.loc[date, 'Close'] = item.close

        pass

    # data = [item.close for item in daily][60::-1]
    # data =  pd.DataFrame(data, columns=[holders_count])

    plt.title('{ts_code} {name}'.format(ts_code=ts_code, name=name), fontsize=100, fontproperties='Heiti TC')
    # sns.lineplot(data=data, palette="tab10", linewidth=1.5)
    # plt.clf()
    mpf.plot(df, type='candle', style=style)
    print('plot {ts_code} {name}'.format(ts_code=ts_code, name=name))