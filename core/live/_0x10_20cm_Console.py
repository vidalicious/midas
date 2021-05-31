# -*- coding: utf-8 -*-
import sys
import os

live_path = os.path.dirname(os.path.realpath(__file__))
core_path = os.path.split(live_path)[0]
root_path = os.path.split(core_path)[0]
parent_path = os.path.split(root_path)[0]
sys.path.append(parent_path)

import time
import grequests
import pandas as pd
import midas.bin.env as env
from midas.core.data.engine import main_session
import midas.core.data.models as models

target_symbols = [
    '300845',
    '300839',
    '300849',
    '300927',
    '300838',
    '300930',
    '300929',
    '300897',
    '300923',
    '300899',
    '300960',
    '300943',
    '300886',
    '300808',
    '300972',
    '300668',
    '300907',
    '300913',
    '300807',
    '300865',
    '300947',
    '300851',
    '300564',
    '300813',
    '300988',
    '300906',
    '300781',
    '300876',
    '300971',
    '300938',
    '300989',
    '300749',
    '300902',
    '300640',
    '300926',
    '300789',
    '300980',
    '300978',
    '300967',
    '300881',
    '300969',
    '300949',
    '300882',
    '300975',
    '300936',
    '300885',
    '300956',
    '300921',
    '300553',
    '300539',
    '300819',
    '300977',
    '300752',
    '300928',
    '300893',
    '300889',
    '300931',
    '300818',
    '300920',
    '300840',
    '300823',
    '300780',
    '300843',
    '300895',
    '300880',
    '300970',
    '300917',
    '300554',
    '300846',
    '300817',
    '300878',
    '300700',
    '300918',
    '300948',
    '300615',
    '300354',
    '300963',
    '300879',
    '300606',
    '300868',
    '300901',
    '300922',
    '300916',
    '300932',
    '300809',
    '300985',
    '300508',
    '300958',
    '300742',
    '300946',
    '300626',
    '300270',
    '300952',
    '300933',
    '300950',
    '300912',
    '300852',
    '300650',
    '300509',
    '300935',
    '300826',
    '300990',
    '300833',
    '300909',
    '300837',
    '300822',
    '300778',
    '300665',
    '300275',
    '300905',
    '300915',
    '300478',
    '300797',
    '300942',
    '300417',
    '300847',
    '300836',
    '300756',
    '300883',
    '300779',
    '300939',
    '300535',
    '300743',
    '300405',
    '300611',
    '300890',
    '300877',
    '300864',
    '300842',
    '300619',
    '300505',
    '300786',
    '300796',
    '300863',
    '300925',
    '300605',
    '300986',
    '300862',
    '300828',
    '300961',
    '300820',
    '300461',
    '300853',
    '300694',
    '300898',
    '300437',
    '300965',
    '300892',
    '300389',
    '300584',
    '300940',
    '300870',
    '300857',
    '300235',
    '300594',
    '300812',
    '300787',
    '300903',
    '300371',
    '300824',
    '300609',
    '300283',
    '300462',
    '300084',
    '300411',
    '300937',
    '300955',
    '300126',
    '300560',
    '300306',
    '300688',
    '300335',
    '300873',
    '300557',
    '300654',
    '300875',
    '300514',
    '300793',
    '300517',
    '300681',
    '300167',
    '300092',
    '300407',
    '300321',
    '300210',
    '300856',
    '300968',
    '300556',
    '300720',
    '300713',
    '300670',
    '300858',
    '300753',
    '300649',
    '300612',
    '300736',
    '300591',
    '300532',
    '300987',
    '300165',
    '300555',
    '300254',
    '300528',
    '300900',
    '300426',
    '300801',
    '300716',
    '300652',
    '300538',
    '300282',
    '300089',
    '300717',
    '300338',
    '300022',
    '300262',
    '300540',
    '300710',
    '300501',
    '300330',
    '300608',
    '300635',
    '300703',
    '300491',
    '300250',
    '300163',
    '300484',
    '300962',
    '300515',
    '300375',
    '300345',
    '300025',
    '300344',
    '300835',
    '300549',
    '300472',
    '300827',
    '300108',
    '300730',
    '300830',
    '300329',
    '300545',
    '300141',
    '300707',
    '300951',
    '300164',
    '300908',
    '300706',
    '300941',
    '300891',
    '300621',
    '300629',
    '300771',
    '300076',
    '300563',
    '300658',
    '300334',
    '300599',
    '300062',
    '300445',
    '300534',
    '300911',
    '300449',
    '300469',
    '300112',
    '300220',
    '300805',
    '300107',
    '300499',
    '300387',
    '300195',
    '300810',
    '300871',
    '300155',
    '300295',
    '300583',
    '300799',
    '300500',
    '300867',
    '300404',
    '300953',
    '300162',
    '300983',
    '300811',
    '300597',
    '300855',
    '300444',
    '300074',
    '300150',
    '300798',
    '300757',
    '300336',
    '300533',
    '300644',
    '300561',
    '300154',
    '300467',
    '300669',
    '300585',
    '300562',
    '300351',
    '300479',
    '300656',
    '300097',
    '300052',
    '300746',
    '300765',
    '300647',
    '300179',
    '300519',
    '300385',
    '300175',
    '300018',
    '300698',
    '300139',
    '300218',
    '300788',
    '300249',
    '300466',
    '300860',
    '300689',
    '300622',
    '300246',
    '300209',
    '300488',
    '300625',
    '300610',
    '300592',
    '300718',
    '300603',
    '300135',
    '300106',
    '300686',
    '300240',
    '300697',
    '300192',
    '300503',
    '300380',
    '300412',
    '300645',
    '300399',
    '300507',
    '300887',
    '300281',
    '300547',
    '300374',
    '300637',
    '300494',
    '300430',
    '300643',
    '300286',
    '300513',
    '300013',
    '300452',
    '300473',
    '300176',
    '300631',
    '300279',
    '300172',
    '300419',
    '300872',
    '300421',
    '300447',
    '300721',
    '300103',
    '300565',
    '300309',
    '300586',
    '300333',
    '300745',
    '300894',
    '300140',
    '300004',
    '300169',
    '300153',
    '300976',
    '300057',
    '300719',
    '300117',
    '300660',
    '300105',
    '300050',
    '300288',
    '300675',
    '300152',
    '300403',
    '300301',
    '300506',
    '300772',
    '300690',
    '300785',
    '300667',
    '300305',
    '300648',
    '300589',
    '300230',
    '300148',
    '300245',
    '300489',
    '300260',
    '300095',
    '300365',
    '300350',
    '300217',
    '300040',
    '300214',
    '300011',
    '300693',
    '300691',
    '300320',
    '300241',
    '300758',
    '300428',
    '300559',
    '300067',
    '300228',
    '300343',
    '300543',
    '300542',
    '300277',
    '300056',
    '300727',
    '300201',
    '300063',
    '300353',
    '300511',
    '300512',
    '300521',
    '300791',
    '300311',
    '300732',
    '300049',
    '300402',
    '300247',
    '300733',
    '300414',
    '300711',
    '300392',
    '300802',
    '300242',
    '300086',
    '300536',
    '300366',
    '300042',
    '300434',
    '300577',
    '300424',
    '300289',
    '300081',
    '300211',
    '300816',
    '300290',
    '300310',
    '300570',
    '300680',
    '300800',
    '300692',
    '300231',
    '300425',
    '300157',
    '300252',
    '300861',
    '300030',
    '300636',
    '300617',
    '300276',
    '300600',
    '300234',
    '300359',
    '300480',
    '300651',
    '300490',
    '300314',
    '300410',
    '300678',
    '300448',
    '300111',
    '300120',
    '300632',
    '300213',
    '300043',
    '300423',
    '300576',
    '300422',
    '300265',
    '300483',
    '300021',
    '300869',
    '300299',
    '300790',
    '300272',
    '300302',
    '300198',
    '300360',
    '300518',
    '300575',
    '300641',
    '300550',
    '300552',
    '300504',
    '300709',
    '300695',
    '300571',
    '300435',
    '300684',
    '300259',
    '300485',
    '300237',
    '300161',
    '300493',
    '300723',
    '300850',
    '300047',
    '300701',
    '300227',
    '300522',
    '300065',
    '300129',
    '300007',
    '300239',
    '300173',
    '300181',
    '300160',
    '300580',
    '300541',
    '300337',
    '300300',
    '300440',
    '300125',
    '300486',
    '300420',
    '300578',
    '300297',
    '300099',
    '300100',
    '300091',
    '300127',
    '300292',
    '300673',
    '300429',
    '300548',
    '300806',
    '300293',
    '300284',
    '300094',
    '300128',
    '300436',
    '300137',
    '300569',
    '300045',
    '300620',
    '300191',
    '300739',
    '300705',
    '300520',
    '300460',
    '300590',
    '300016',
    '300199',
    '300291',
    '300683',
    '300386',
    '300183',
    '300200',
    '300551',
    '300032',
    '300364',
    '300471',
    '300130',
    '300384',
    '300349',
    '300019',
    '300075',
    '300708',
    '300331',
    '300248',
    '300194',
    '300427',
    '300205',
    '300761',
    '300304',
    '300109',
    '300322',
    '300453',
    '300324',
    '300159',
    '300766',
    '300187',
    '300381',
    '300184',
    '300039',
    '300196',
    '300332',
    '300189',
    '300910',
    '300821',
    '300400',
    '300066',
    '300442',
    '300341',
    '300317',
    '300010',
    '300174',
    '300256',
    '300273',
    '300008',
    '300497',
    '300266',
    '300409',
    '300602',
    '300981',
    '300342',
    '300729',
    '300328',
    '300287',
    '300762',
    '300263',
    '300261',
    '300531',
    '300397',
    '300664',
    '300572',
    '300020',
    '300439',
    '300121',
    '300093',
    '300258',
    '300378',
    '300687',
    '300177',
    '300190',
    '300046',
    '300526',
    '300464',
    '300768',
    '300468',
    '300815',
    '300393',
    '300443',
    '300255',
    '300657',
    '300416',
    '300510',
    '300516',
    '300455',
    '300587',
    '300215',
    '300053',
    '300145',
    '300197',
    '300080',
    '300465',
    '300203',
    '300147',
    '300741',
    '300624',
    '300792',
    '300048',
    '300659',
    '300061',
    '300355',
    '300396',
    '300110',
    '300319',
    '300303',
    '300377',
    '300031',
    '300642',
    '300388',
    '300391',
    '300663',
    '300307',
    '300078',
    '300475',
    '300755',
    '300523',
    '300170',
    '300607',
    '300158',
    '300131',
    '300581',
    '300102',
    '300776',
    '300267',
    '300005',
    '300829',
    '300696',
    '300566',
    '300041',
    '300193',
    '300232',
    '300206',
    '300525',
    '300280',
    '300219',
    '300634',
    '300055',
    '300238',
    '300866',
    '300973',
    '300666',
    '300138',
    '300492',
    '300006',
    '300368',
    '300222',
    '300481',
    '300134',
    '300441',
    '300888',
    '300098',
    '300382',
    '300406',
    '300036',
    '300318',
    '300113',
    '300579',
    '300438',
    '300593',
    '300352',
    '300470',
    '300208',
    '300919',
    '300825',
    '300180',
    '300401',
    '300979',
    '300702',
    '300415',
    '300456',
    '300841',
    '300229',
    '300738',
    '300149',
    '300002',
    '300803',
    '300233',
    '300712',
    '300116',
    '300735',
    '300770',
    '300722',
    '300182',
    '300166',
    '300674',
    '300085',
    '300027',
    '300082',
    '300432',
    '300769',
    '300398',
    '300394',
    '300114',
    '300627',
    '300079',
    '300068',
    '300679',
    '300740',
    '300596',
    '300527',
    '300653',
    '300133',
    '300225',
    '300767',
    '300035',
    '300487',
    '300185',
    '300567',
    '300358',
    '300616',
    '300457',
    '300639',
    '300224',
    '300151',
    '300087',
    '300459',
    '300119',
    '300775',
    '300598',
    '300132',
    '300573',
    '300638',
    '300613',
    '300101',
    '300326',
    '300188',
    '300323',
    '300379',
    '300123',
    '300348',
    '300451',
    '300748',
    '300633',
    '300502',
    '300773',
    '300315',
    '300026',
    '300671',
    '300236',
    '300257',
    '300346',
    '300783',
    '300226',
    '300763',
    '300662',
    '300034',
    '300777',
    '300682',
    '300054',
    '300072',
    '300369',
    '300118',
    '300017',
    '300271',
    '300143',
    '300474',
    '300726',
    '300458',
    '300672',
    '300395',
    '300390',
    '300296',
    '300298',
    '300957',
    '300376',
    '300058',
    '300024',
    '300747',
    '300083',
    '300212',
    '300327',
    '300339',
    '300294',
    '300476',
    '300568',
    '300618',
    '300737',
    '300171',
    '300630',
    '300832',
    '300070',
    '300168',
    '300009',
    '300244',
    '300463',
    '300623',
    '300418',
    '300724',
    '300685',
    '300088',
    '300373',
    '300751',
    '300115',
    '300725',
    '300136',
    '300482',
    '300383',
    '300073',
    '300001',
    '300037',
    '300308',
    '300363',
    '300253',
    '300676',
    '300357',
    '300033',
    '300146',
    '300896',
    '300251',
    '300677',
    '300999',
    '300699',
    '300628',
    '300144',
    '300285',
    '300661',
    '300207',
    '300529',
    '300558',
    '300496',
    '300003',
    '300012',
    '300759',
    '300316',
    '300595',
    '300408',
    '300498',
    '300413',
    '300454',
    '300782',
    '300450',
    '300601',
    '300347',
    '300142',
    '300274',
    '300433',
    '300124',
    '300122',
    '300014',
    '300760',
    '300059',
    '300015',
    '300750'
]

target_symbols = list(set(target_symbols))

def run():

    symbol2code = {}
    stock_map = {}
    for stock in main_session.query(models.DailyBasic).all():
        ts_code = stock.ts_code
        market = ts_code.split('.')[1].lower()
        symbol = ts_code.split('.')[0]
        code = '{market}{symbol}'.format(market=market, symbol=symbol)
        symbol2code[symbol] = code
        stock_map[code] = {
            'circ_mv': float(stock.circ_mv)
        }

    batch_size = 500
    req_list = []
    for i in range(0, len(target_symbols), batch_size):
        keys = []
        for symbol in target_symbols[i:i+batch_size]:
            query_key = symbol2code[symbol]
            keys.append(query_key)

        req_list.append(grequests.get('http://hq.sinajs.cn/list={}'.format(','.join(keys))))

    while True:
        time_a = time.time()
        try:
            responses = grequests.map(req_list)
            print('====== {} ======'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            displays = []
            for response in responses:
                res = response.text.strip().split(';\n')
                for i in res:
                    j = i.split(',')
                    name = j[0].split('="')[1]
                    code = j[0].split('="')[0].split('_')[-1]
                    yesterday_closing_price = float(j[2])
                    current_price = float(j[3])
                    today_max_price = float(j[4])
                    buy_one_price = float(j[6])
                    buy_one_vol = float(j[10])
                    today_limit_price = round(yesterday_closing_price * 1.2, 2)
                    chg = (current_price / yesterday_closing_price - 1)
                    chg_display = '{}%'.format(round(chg*100, 2))
                    circ_mv = stock_map[code]['circ_mv']

                    if_display = False
                    type = 1
                    if today_max_price == today_limit_price: #摸过板的
                        if_display = True
                        if buy_one_price < today_limit_price: #开板
                            if_display = True
                        elif buy_one_price * buy_one_vol < 10000000: #封单小于1kw
                            if_display = True
                            type = 2

                    elif chg > 0.1:
                        if_display = True

                    # if_display = True

                    if if_display:
                        if type == 2:
                            displays.append({
                                'note': '{code}\t{name}\tchg:{chg}\tprice:{price}\tcirc_mv:{circ_mv}亿\t封单:{vol}手'.format(code=code, name=name, chg=chg_display,
                                    price=round(current_price, 2), circ_mv=int(circ_mv), vol=int(buy_one_vol / 100)),
                                'chg': chg
                            })
                        else:
                            displays.append({
                                'note': '{code}\t{name}\tchg:{chg}\tprice:{price}\tcirc_mv:{circ_mv}亿'.format(code=code, name=name, chg=chg_display,
                                    price=round(current_price, 2), circ_mv=int(circ_mv)),
                                'chg': chg
                            })

            displays.sort(key=lambda x: x['chg'], reverse=False)
            notes = [i['note'] for i in displays]
            print('\n'.join(notes))
        except Exception as e:
            print(e)
            continue
        time_b = time.time()
        cost = time_b - time_a
        time.sleep(1 - cost)


if __name__ == '__main__':
    run()