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
                '酿酒':4,
                '食品饮料':4,
                '芯片':3,
                '锂电池':3,
                '医药':3,
                '医美':3,
                '化工':3,
                '房地产':2,
                '煤炭':2,
                '服装家纺':2,
                '碳中和':2,
                '养老':2,
                '参股金融':2
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
        }, {
            'date': 20210609,
            'concepts': {
                '化工':12,
                '华为':7,
                '军工':6,
                '酿酒':4,
                '芯片':3,
                '煤炭':2
            }
        }, {
            'date': 20210610,
            'concepts': {
                '华为':23,
                '锂电池':6,
                '光伏':6,
                '国产软件':6,
                '网红':4,
                '军工':3,
                '芯片':2,
                '航运':2
            }
        }, {
            'date': 20210611,
            'concepts': {
                '华为':19,
                '浙江':11,
                '碳中和':7,
                '光伏':3,
                '有色':2,
                '化工':2
            }
        }, {
            'date': 20210615,
            'concepts': {
                '华为':14,
                '化工':4,
                '虚拟现实':3,
                '浙江':3,
                '芯片':2,
                '锂电池':2,
                '新能源汽车':4
            }
        }, {
            'date': 20210616,
            'concepts': {
                '华为':7,
                '芯片':4,
                '石油石化':3,
                '军工':3
            }
        }, {
            'date': 20210617,
            'concepts': {
                '芯片':17,
                '碳中和':5,
                '酿酒':4,
                '华为':4,
                '医美':3,
                '无线耳机':2
            }
        }, {
            'date': 20210618,
            'concepts': {
                '芯片':9,
                '新能源汽车':7,
                '锂电池':6,
                '华为':6,
                '化工':3,
                '医药':2,
                '酿酒':2
            }
        }, {
            'date': 20210621,
            'concepts': {
                '碳中和':9,
                '华为':8,
                '新能源汽车':6,
                '芯片':5,
                '医药':5,
                '军工':5,
                '锂电池':3,
                '医美':3,
                '钢铁':2,
                '光伏':2
            }
        }, {
            'date': 20210622,
            'concepts': {
                '新能源汽车':8,
                '军工':5,
                '光伏':4,
                '华为':4,
                '医药':3,
                '家电':3,
                'LED':3,
                '化工':3,
                '芯片':2,
                '煤炭':2,
                '有色':2,
                '食品饮料':2
            }
        }, {
            'date': 20210623,
            'concepts': {
                '新能源汽车': 7,
                '芯片':4,
                '酿酒':3,
                '印制电路板':3,
                '华为':3,
                '消费电子':3,
                '锂电池':2,
                '环保':2,
                '光伏':2,
                '碳中和':2,
                '汽车电子':2
            }
        }, {
            'date': 20210624,
            'concepts': {
                '光伏':25,
                '新能源汽车':4,
                '芯片':2,
                '苹果':2,
                '服装家纺':2,
                '碳中和':2,
                '浙江':2
            }
        }, {
            'date': 20210625,
            'concepts': {
                '光伏':10,
                '化工':8,
                '芯片':4,
                '新能源汽车':4,
                '酿酒':3,
                '医药':3,
                '银行':2,
                '军工':2,
                '煤炭':2,
                '证券':2,
                '互联网金融':2,
                '参股金融':2
            }
        }, {
            'date': 20210628,
            'concepts': {
                '碳中和':6,
                '芯片':5,
                '锂电池':5,
                '酿酒':5,
                '光伏':5,
                '华为':5,
                '医药':4,
                '医美':3,
                '农业':3,
                '5G':2,
                '服装家纺':2,
                '化工':2
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