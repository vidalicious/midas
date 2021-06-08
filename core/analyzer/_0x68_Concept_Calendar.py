import numpy as np
from pandas import DataFrame
import matplotlib.pyplot as plt
import seaborn as sns
import midas.bin.env as env

plt.rcParams['font.sans-serif'] = ['Heiti TC']  # 中文字体设置-黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题
sns.set(font='Heiti TC')

def main():
    raw_data = [
        {
            'date': 20210601,
            'concepts': {
                '多胎':9,
                ''
            }
        }, {
            'date':20210602,
            'concepts':{
                '碳中和':7,
                '服装家纺':4,
                '医药':3,
                '石油石化':2,
                '煤炭':2,
                '海航系':2,
                '汽车配件':2
            }
        }, {
            'date':20210603,
            'concepts':{
                '上海':15,
                '5G':4,
                '碳中和':4,
                '锂电池':3,
                '芯片':2,
                '酿酒':2,
                '煤炭':2,
                '有色':2,
                '服装家纺':2,
                '金融科技':2
            }
        }, {
            'date':20210604,
            'concepts':{
                '锂电池':15,
                '酿酒':5,
                '新能源汽车':4,
                '芯片':2,
                '5G':2,
                '医药':2,
                '服装家纺':2
            }
        }, {
            'date':20210607,
            'concepts':{
                '华为':10,
                '酿酒':9,
                '芯片':8,
                '锂电池':5,
                '化工':5,
                '医药':2,
            }
        }, {
            'date': 20210608,
            'concepts': {
                '华为': 10,
                '网红': 5,
                '上海': 4,
                '新能源汽车': 3,
                '军工': 3,
                '碳中和': 3,
                '芯片': 2,
                '5G': 2,
                '锂电池': 2,
                '充电桩': 2
            }
        }
    ]

    dates = list()
    concepts = set()
    for item in raw_data:
        dates.append(item['date'])
        for k, v in item['concepts'].items():
            concepts.add(k)

    data = dict()
    for i in range(len(dates)):
        date = dates[i]
        data[date] = dict()
        for concept in concepts:
            if concept in raw_data[i]['concepts'].keys():
                data[date][concept] = raw_data[i]['concepts'][concept]
            else:
                data[date][concept] = 0

    data_frame = DataFrame()
    for k, v in data.items():
        for sub_k, sub_v in v.items():
            data_frame.loc[k, sub_k] = sub_v

    LAST_MARKET_DATE = dates[-1]

    fig = plt.figure(figsize=(len(dates) * 1, len(concepts) * 0.5))
    plt.subplots_adjust(left=5/(5 + len(dates)), right=1, top=1, bottom=5/(5 + len(concepts)))
    data_frame = data_frame.T
    data_frame = data_frame.sort_index()
    sns.heatmap(data_frame, annot=True, cmap="Blues", linewidths=.5)
    fig.tight_layout()
    plt.xticks(rotation=90)
    plt.savefig('{fupan_path}/{date}_calendar.png'.format(fupan_path=env.fupan_path, date=LAST_MARKET_DATE))

    print()


    pass



if __name__ == '__main__':
    main()