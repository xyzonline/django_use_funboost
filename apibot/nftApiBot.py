import json
import os
import traceback
import time
import requests

HEADERS = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'origin': 'http://localhost:3005',
    'referer': 'http://localhost:3005',
    'Content-Type': 'application/json',
}

userCenter = "http://a8.gitez.cc:31010/v1"
nftMarket = "http://a8.gitez.cc:31011/v1"
walletProxy = "http://a8.gitez.cc:31015"

userName = "uat-006@test.com"
password = "123456"
twiToken = ""

def gettimestr():
    try:
        timestr = time.strftime("%Y-%m-%d %H:%M:%S   ", time.gmtime(time.time()+8*3600))
        return timestr
    except Exception as e:
        return ""

def apiGet(host, api, params):
    url = host + api
    if twiToken != "":
        HEADERS["Authorization"] = "Bearer " + twiToken
    rsp = requests.get(url, headers=HEADERS, timeout=30, params=params)
    ret = rsp.json()
    print(gettimestr(), api, ret["code"])
    return ret


def apiPost(host, api, form):
    url = host + api
    if twiToken != "":
        HEADERS["Authorization"] = "Bearer " + twiToken
    rsp = requests.post(url, headers=HEADERS, timeout=30, json=form)
    if rsp.status_code == 200:
        ret = rsp.json()
        print(gettimestr(), api, ret["code"])
        return ret
    else:
        print(gettimestr(), api, rsp.status_code, rsp)
        return None

try:
    apiGet(nftMarket, "/public/highlight/projects", {"type": "top", "page": 1, "size": 2})
    rsp = apiPost(userCenter, "/user/login", {"password": password, "email": userName})
    if rsp != None:
        twiToken = rsp["data"]["token"]
        rsp = apiGet(walletProxy, "/wallet/balance", {})
        if rsp["code"] == 0:
            print(rsp["data"]["ethereum"][0]["balance"], "ETH")
        # rsp = apiGet(nftMarket, "/public/listing", {"listing_id": "LIST283119900213317"})
        # print(rsp)
        for i in range(4):
            rsp = apiGet(nftMarket, "/public/listing", {"listing_id": "LIST283131338907717"})
            if rsp["code"] == 0:
                print("current_price", rsp["data"]["current_price"])
                print("BID",str(float(rsp["data"]["current_price"])*1.051))
                rsp = apiPost(nftMarket, "/trade/bid", {"listing_id": "LIST283131338907717",
                                                   "price": str(float(rsp["data"]["current_price"])*1.051),
                                                   "price_unit": "ETH",
                                                   "amount": 1,
                                                   "two_fa_code": "192939",
                                                   "nonce": str(time.time())
                                                   })
                print(rsp)
except Exception as e1:
    traceback.print_exc()
