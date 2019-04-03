# -*- coding: utf-8 -*-
import json
import time

import tushare as ts
from pandas import DataFrame
import numpy as np

import midas.midas.api_pro as api
import midas.midas.data.models as models
from midas.midas.data.engine import main_session


def main():
    pro = ts.pro_api()

    main_session.query(models.ConceptPro).delete()
    main_session.commit()
    concepts = pro.concept()
    for i in range(len(concepts)):
        a_concept = models.ConceptPro(code=concepts.loc[i, 'code'],
                                      name=concepts.loc[i, 'name'])
        main_session.add(a_concept)
    main_session.commit()

    print('##### async concept finished #####')

    for count, concept in enumerate(main_session.query(models.ConceptPro).all()):
        try:
            df = pro.concept_detail(id=concept.code, fields='ts_code,name')
        except Exception as e:
            print('excetion in {}'.format(count))
            continue

        for i in range(len(df)):
            a_detail = models.ConceptDetailPro(code=concept.code,
                                               ts_code=df.loc[i, 'ts_code'],
                                               name=df.loc[i, 'name'])
            main_session.add(a_detail)
        main_session.commit()
        print('##### {i} #####'.format(i=count))
        time.sleep(0.5)


if __name__ == '__main__':
    main()


