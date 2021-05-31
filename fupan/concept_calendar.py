import numpy as np
from pandas import DataFrame
import matplotlib.pyplot as plt
import seaborn as sns
import midas.core.data.models as models
from midas.core.data.engine import main_session
import midas.bin.env as env

plt.rcParams['font.sans-serif'] = ['Heiti TC']  # 中文字体设置-黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题
sns.set(font='Heiti TC')

def main():
    raw_data = [
        {
            
        }, {
            'date': 20210524,
            'concepts': ['钠电池', '碳中和', '酿酒', '房地产', '新能源汽车', '网红', '二胎', '国产软件']
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
        },
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
                for j in range(max(0, i - 4), i + 1):
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

    daily001 = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == '000001.SZ').order_by(models.DailyPro.trade_date.desc()).all()
    LAST_MARKET_DATE = daily001[0].trade_date

    fig = plt.figure(figsize=(len(dates) * 0.8, len(concepts) * 0.35))
    plt.subplots_adjust(left=5/(5 + len(dates)), right=1, top=1, bottom=5/(5 + len(concepts)))
    sns.heatmap(data_frame.T, cmap="Blues", linewidths=.5)
    fig.tight_layout()
    plt.savefig('{fupan_path}/{date}_calendar.png'.format(fupan_path=env.fupan_path, date=LAST_MARKET_DATE))


if __name__ == '__main__':
    main()