# -*- coding: utf-8 -*-
import requests


headers = {
    'Content-Type': 'application/json; charset=UTF-8',
    'Authorization': 'APPCODE ' + 'a541d723a1874f329f0e63dd3c6cdac4'
}

json = {
    "prod_code_obj_grp": [
        {
            "prod_code": "300362",
            "hq_type_code": "XSHE"
        },
        {
            "prod_code": "300218",
            "hq_type_code": "XSHE"
        },
    ]
}
url = 'http://costdis.market.alicloudapi.com/quote/v2/qplus/cost_distribution/get_stock_chip'
a = requests.post(url=url, headers=headers, json=json)
print(a.json())