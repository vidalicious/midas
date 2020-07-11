

def plot_gether(data_frame, last_date):
    columns = 5
    rows = math.ceil(len(data_frame) / columns)

    plt.figure(figsize=(columns * 5, rows * 5 / 2))
    sns.set(style="whitegrid")
    for i in range(len(data_frame)):
        ts_code = data_frame.loc[i, 'ts_code']
        name = data_frame.loc[i, 'name']
        plt.subplot(rows, columns, i + 1)
        plot_single(ts_code=ts_code, name=name, last_date=last_date, holders_count=data_frame.loc[i, COL_HOLDERS_COUNT])

    plt.tight_layout()
    plt.savefig('../../buffer/aggressive_break/{date}_aggressive_break.png'.format(date=last_date))


def plot_single(ts_code, name, last_date, holders_count):
    daily = main_session.query(models.DailyPro).filter(models.DailyPro.ts_code == ts_code,
                                                       models.DailyPro.trade_date <= last_date).order_by(
        models.DailyPro.trade_date.desc()).limit(sampling_count).all()

    data = [item.close for item in daily][60::-1]
    data =  pd.DataFrame(data, columns=[holders_count])

    plt.title('{ts_code} {name}'.format(ts_code=ts_code, name=name), fontsize=100, fontproperties='Heiti TC')
    sns.lineplot(data=data, palette="tab10", linewidth=1.5)
    # plt.clf()
    print('plot {ts_code} {name}'.format(ts_code=ts_code, name=name))