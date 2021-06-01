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
            'date': 20210427,
            'concepts': ['二胎', '服装家纺', '医美', '医药', '食品饮料', '区块链']
        }, {
            'date': 20210428,
            'concepts': ['医美', '医药', '二胎', '酿酒', '煤炭', '服装家纺', '旅游']
        }, {
            'date': 20210429,
            'concepts': ['医美', '服装家纺', '芯片', '酿酒', '二胎', '化工']
        }, {
            'date': 20210430,
            'concepts': ['医美', '医药', '锂电池', '疫苗', '文化传媒']
        }, {
            'date': 20210506,
            'concepts': ['钢铁', '锂电池', '医美', '化工', '区块链', '网红', '军工', '碳中和', '新能源汽车', '煤炭', '有色', '多胎', '百年庆典', '新能源汽车']
        }, {
            'date': 20210507,
            'concepts': ['钢铁', '煤炭', '有色', '医美', '区块链', '黄金', '多胎', '化工', '百年庆典']
        }, {
            'date': 20210510,
            'concepts': ['钢铁', '有色', '多胎', '医美', '煤炭', '养老', '区块链', '锂电池', '预制菜', '疫苗', '石油石化', '化工', '百年庆典', '新能源汽车', '金刚石']
        }, {
            'date': 20210511,
            'concepts': ['养老', '医美', '碳中和', '区块链', '酿酒', '医药', '有色', '食品饮料', '钢铁', '金刚石', '上海自贸区', '民营医院']
        }, {
            'date': 20210512,
            'concepts': ['医美', '新能源汽车', '华为', '化工', '养老', '天然气', '服装家纺', '百年庆典', '钢铁', '芯片', '新能源汽车', '有色', '农业', '电子烟']
        }, {
            'date': 20210513,
            'concepts': ['医药', '房地产', '医美', '多胎', '华为', '食品饮料', '养老']
        }, {
            'date': 20210514,
            'concepts': ['证券', '华为', '碳中和', '食品饮料', '文化传媒', '环保', '家电', '互联网金融', '新能源汽车', '医药', '酿酒', '服装家纺', '医美', '机器人',
                         '金融科技']
        }, {
            'date': 20210517,
            'concepts': ['新能源汽车', '数字能源', '证券', '互联网金融', '医美', '虚拟现实', '食品饮料']
        }, {
            'date': 20210518,
            'concepts': ['石油石化', '医美', '碳中和', '新能源汽车', '食品饮料', '数字能源', '网红', '5G', '锂电池', '房地产', '酿酒', '黄金', '环保', '核电',
                         '食品饮料', '电子烟']
        }, {
            'date': 20210519,
            'concepts': ['锂电池', '新能源汽车', '碳中和', '虚拟现实', '医美', '网红', '医药', '家电', '数字能源', '防脱发']
        }, {
            'date': 20210520,
            'concepts': ['碳中和', '酿酒', '芯片', '充电桩', '证券', '国产软件', '医美', '体育', '网红']
        }, {
            'date': 20210521,
            'concepts': ['碳中和', '百年庆典', '锂电池', '金融科技', '充电桩', '钢铁', '有色', '国产软件', '网红']
        }, {
            'date': 20210524,
            'concepts': ['钠电池', '碳中和', '酿酒', '房地产', '新能源汽车', '网红', '多胎', '国产软件']
        }, {
            'date': 20210525,
            'concepts': ['医药', '证券', '碳中和', '化工', '网红', '军工', '煤炭', '服装家纺', '国产软件', '医美']
        },{
            'date': 20210526,
            'concepts': ['可降解', '碳中和', '跨境电商', '参股金融', '新能源汽车', '医美', '食品饮料', '锂电池', '酿酒']
        },{
            'date': 20210527,
            'concepts': ['芯片', '碳中和', '医药', '光刻胶', '医美', '跨境电商', '食品饮料', '有色', '酿酒', '游戏', '可降解', '智能家居']
        }, {
            'date': 20210528,
            'concepts': ['外销', '碳中和', '医美', '锂电池', '化工', '汽车配件', '华为', '参股金融']
        }, {
            'date': 20210531,
            'concepts': ['碳中和', '锂电池', '汽车配件', '芯片', '医药', '多胎', '医美', '网红', '光伏', '机器人', '自行车', '食品饮料', '云计算', '基础建设']
        }, {
            'date': 20210601,
            'concepts': ['多胎', '酿酒', '食品饮料', '芯片', '锂电池', '医药', '医美', '化工', '房地产', '煤炭', '服装家纺', '碳中和', '养老', '参股金融']
        }
    ]

    dates = list()
    concepts = set()
    for item  in raw_data:
        dates.append(item['date'])
        for concept in item['concepts']:
            concepts.add(concept)

    data = dict()
    for i in range(len(dates)):
        date = dates[i]
        data[date] = dict()
        for concept in concepts:
            if concept in raw_data[i]['concepts']:
                count = 0
                for j in range(max(0, i - 9), i + 1):
                    if concept in raw_data[j]['concepts']:
                        count += 1
                data[date][concept] = count
            else:
                data[date][concept] = 0
        pass

    data_frame = DataFrame()
    for k, v in data.items():
        for sub_k, sub_v in v.items():
            data_frame.loc[k, sub_k] = sub_v

    LAST_MARKET_DATE = dates[-1]

    fig = plt.figure(figsize=(len(dates) * 0.6, len(concepts) * 0.35))
    plt.subplots_adjust(left=5/(5 + len(dates)), right=1, top=1, bottom=5/(5 + len(concepts)))
    data_frame = data_frame.T
    data_frame = data_frame.sort_index()
    sns.heatmap(data_frame, cmap="Blues", linewidths=.5)
    fig.tight_layout()
    plt.savefig('{fupan_path}/{date}_calendar.png'.format(fupan_path=env.fupan_path, date=LAST_MARKET_DATE))


if __name__ == '__main__':
    main()