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
            'date': 20210506,
            'concepts': {
                '钢铁':10,
                '锂电池':5,
                '医美':4,
                '化工':4,
                '区块链':3,
                '网红':3,
                '军工':3,
                '碳中和':3,
                '新能源汽车':4,
                '煤炭':2,
                '有色':2,
                '二胎':2,
                '百年庆典':2
            }
        }, {
            'date': 20210507,
            'concepts': {
                '钢铁': 7,
                '煤炭':5,
                '有色':4,
                '医美':4,
                '区块链':4,
                '黄金':3,
                '二胎':2,
                '化工':2,
                '百年庆典':2
            }
        }, {
            'date': 20210510,
            'concepts': {
                '钢铁':11,
                '有色':9,
                '二胎':9,
                '医美':6,
                '煤炭':5,
                '养老':5,
                '区块链':5,
                '锂电池':3,
                '预制菜':3,
                '疫苗':2,
                '石油石化':2,
                '化工':2,
                '百年庆典':2,
                '新能源汽车':2,
                '金刚石':2
            }
        }, {
            'date': 20210511,
            'concepts': {
                '养老':9,
                '医美':3,
                '碳中和':3,
                '区块链':3,
                '酿酒':2,
                '医药':2,
                '有色':2,
                '食品饮料':2,
                '钢铁':2,
                '金刚石':2,
                '上海自贸区':2,
                '民营医院':2
            }
        }, {
            'date': 20210512,
            'concepts': {
                '医美':12,
                '新能源汽车':12,
                '华为':6,
                '化工':6,
                '养老':4,
                '天然气':3,
                '服装家纺':3,
                '百年庆典':3,
                '钢铁':3,
                '芯片':2,
                '有色':2,
                '农业':2,
                '电子烟':2
            }
        }, {
            'date': 20210513,
            'concepts': {
                '医药':9,
                '房地产':3,
                '医美':3,
                '二胎':2,
                '华为':2,
                '食品饮料':2,
                '养老':2
            }
        }, {
            'date': 20210514,
            'concepts': {
                '证券':9,
                '华为':8,
                '碳中和':6,
                '食品饮料':6,
                '文化传媒':3,
                '环保':3,
                '家电':3,
                '互联网金融':3,
                '新能源汽车':3,
                '医药':3,
                '酿酒':2,
                '服装家纺':2,
                '医美':2,
                '机器人':2,
                '金融科技':2
            }
        }, {
            'date': 20210517,
            'concepts': {
                '新能源汽车':4,
                '数字能源':3,
                '证券':2,
                '互联网金融':2,
                '医美':2,
                '虚拟现实':2,
                '食品饮料':2
            }
        }, {
            'date': 20210518,
            'concepts': {
                '石油石化':5,
                '医美':5,
                '碳中和':5,
                '新能源汽车':4,
                '食品饮料':6,
                '数字能源':4,
                '网红':3,
                '5G':2,
                '锂电池':2,
                '房地产':2,
                '酿酒':2,
                '黄金':2,
                '环保':2,
                '核电':2,
                '电子烟':2
            }
        }, {
            'date': 20210519,
            'concepts': {
                '锂电池':7,
                '新能源汽车':4,
                '碳中和':4,
                '虚拟现实':4,
                '医美':3,
                '网红':3,
                '医药':2,
                '家电':2,
                '数字能源':2,
                '防脱发':2,
                '广电网':2
            }
        }, {
            'date': 20210520,
            'concepts': {
                '碳中和':5,
                '酿酒':4,
                '芯片':3,
                '充电桩':2,
                '证券':2,
                '国产软件':2,
                '医美':2,
                '体育产业':2,
                '网红':2
            }
        }, {
            'date': 20210521,
            'concepts': {
                '碳中和':16,
                '百年庆典':4,
                '锂电池':3,
                '金融科技':3,
                '充电桩':2,
                '钢铁':2,
                '有色':2,
                '国产软件':2,
                '网红':2
            }
        }, {
            'date': 20210524,
            'concepts': {
                '钠电池':7,
                '碳中和':13,
                '酿酒':5,
                '房地产':3,
                '新能源汽车':2,
                '网红':2,
                '二胎':2,
                '国产软件':2
            }
        }, {
            'date': 20210525,
            'concepts': {
                '医药':7,
                '证券':4,
                '碳中和':3,
                '化工':3,
                '网红':2,
                '军工':2,
                '煤炭':2,
                '服装家纺':2,
                '国产软件':2,
                '医美':2
            }
        }, {
            'date': 20210526,
            'concepts': {
                '可降解':11,
                '碳中和':7,
                '跨境电商':4,
                '参股金融':4,
                '新能源汽车':3,
                '医美':3,
                '食品饮料':3,
                '锂电池':2,
                '酿酒':2
            }
        }, {
            'date': 20210527,
            'concepts': {
                '芯片': 10,
                '碳中和':7,
                '医药':5,
                '光刻胶':4,
                '医美':3,
                '跨境电商':3,
                '食品饮料':3,
                '有色':2,
                '酿酒':2,
                '游戏':2,
                '可降解':2,
                '智能家居':2
            }
        }, {
            'date': 20210528,
            'concepts': {
                '外销': 7,
                '碳中和': 5,
                '医美': 4,
                '锂电池': 3,
                '化工': 3,
                '汽车配件': 2,
                '华为': 2,
                '参股金融': 2
            }
        }, {
            'date': 20210531,
            'concepts': {
                '碳中和':13,
                '锂电池':7,
                '汽车配件':5,
                '芯片':4,
                '医药':6,
                '多胎':4,
                '医美':4,
                '网红':4,
                '光伏':2,
                '机器人':2,
                '自行车':2,
                '食品饮料':2,
                '云计算':2,
                '基础建设':2
            }
        }, {
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