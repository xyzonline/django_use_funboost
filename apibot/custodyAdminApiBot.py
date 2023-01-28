import json
import os
import traceback
import time
import requests
import json
from typing import Tuple, Dict
from pymailtm import MailTm, Account
from pymailtm.pymailtm import generate_username, CouldNotGetAccountException, InvalidDbAccountException, open_webbrowser, Message

import onetimepass as otp
import datetime
import ezhashlib
import hmac

from apibot import config


fq_proxy = config.fq_proxy
HEADERS = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    # 'origin': 'http://localhost:3005',
    # 'referer': 'http://localhost:3005',
    'Content-Type': 'application/json',
}

twiToken = ""
userInfo = None

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
    rsp = requests.get(url, headers=HEADERS, timeout=30, params=params, proxies=fq_proxy)
    ret = rsp.json()
    print(gettimestr(), api, ret["respCode"])
    return ret


def apiPost(host, api, form):
    url = host + api
    # print("params", api, form)
    if twiToken != "":
        HEADERS["Authorization"] = "Bearer " + twiToken
    rsp = requests.post(url, headers=HEADERS, timeout=30, json=form, proxies=fq_proxy)
    if rsp.status_code == 200:
        ret = rsp.json()
        print(gettimestr(), api, ret["respCode"])
        return ret
    else:
        print(gettimestr(), api, rsp.status_code, rsp)
        return None

# mail.tm api
# address, password, response = create_new_account()
def create_new_account() -> Tuple[str, str, Dict[str, str]]:
    """ use MailTm._make_account_request to create a new random account """
    mt = MailTm()
    domain = mt._get_domains_list()[0]
    username =  generate_username(1)[0].lower()
    address = f"{username}@{domain}"
    password = mt._generate_password(6)
    response = mt._make_account_request("accounts", address, password)
    return address, password, response

def create_new_account(username, password) -> Tuple[str, str, Dict[str, str]]:
    """ use MailTm._make_account_request to create a new random account """
    mt = MailTm()
    domain = mt._get_domains_list()[0]
    # username =  generate_username(1)[0].lower()
    address = f"{username}@{domain}"
    # password = mt._generate_password(6)
    response = mt._make_account_request("accounts", address, password)
    return address, password, response

def regNewMailAccount(username, password_):
    address, password, response = create_new_account(username, password_)
    print("address:", address)
    print("password:", password)
    print("response:")
    print(json.dumps(response, indent=4, separators=(', ', ': '), ensure_ascii=False))

def find2FACodeFromMailBody(html):
    findstring = 'Verification Code</td>\r\n                        </tr>\r\n                        <tr>\r\n                          <td align="center" style="\r\n                                font-size: 28px;\r\n                                color: #555555;\r\n                                font-weight: bold;\r\n                              ">\r\n                            '
    pos1 = html.find(findstring)
    # print("-----------", pos1)
    if pos1 > 0 :
        code = html[pos1 + len(findstring):pos1 + len(findstring) + 6]
        # print("-----code------", code)
        return code
    return ''

def get2FACode(mailAccount, mailPass, startTimeStamp, debug = False):
    account = Account("", mailAccount, mailPass)
    # print(account.id_)
    msg = account.get_messages(1)
    for message_data in msg:
        if message_data.subject == "ON1ON Security Verification":
            if startTimeStamp < datetime.datetime.fromisoformat(message_data.data["createdAt"]).timestamp():
                if debug:
                    print("id:", message_data.id_)
                    print("seen:", message_data.data["seen"])
                    print("from:", message_data.from_["address"])
                    # print("to:", message_data.to)
                    print("subject:", message_data.subject)
                # print("text:", message_data.text)
                code = find2FACodeFromMailBody(message_data.html[0])
                if debug:
                    if code == '':
                        print("html:", message_data.html)
                    else:
                        print("2FA Code:", code)
                    print("createdAt:", message_data.data["createdAt"])
                    print("createdAt:", datetime.datetime.fromisoformat(message_data.data["createdAt"]).timestamp())
                    print("")
                # for message_item in message_data.data:
                #     print(message_item, message_data.data[message_item])
                    print("-------------------------")
                    print("")
                return code
    return ''

def getGACode(secret):
    return otp.get_totp(secret, True)

def custodyLoginGet2FA(hostUrl, userName, password, isAdmin = False):
    api = "login/send2FacodeByLogin"
    # print("sha256", ezhashlib.sha256(password))
    rsp = apiPost(hostUrl, api, {"password": ezhashlib.sha256(password), "mail": userName, "isAdmin": isAdmin})
    if rsp != None:
        if rsp["respCode"] == 0:
            return rsp["respCode"] == 0
        else:
            print(gettimestr(), "error", api, rsp)
    return False



def custodyLoginBy2FA(hostUrl, userName, facode):
    global userInfo, twiToken
    api = "login/login2Facode"
    rsp = apiPost(hostUrl, api, {"facode": facode, "mail": userName})
    if rsp != None:
        print(api, rsp)
        if rsp["respCode"] == 0:
            userInfo = rsp["content"]
            twiToken = rsp["content"]["jwtToken"]
            return True
    return False

def custodyApiCall(hostUrl, api, data, debug = False):
    rsp = apiPost(hostUrl, api, data)
    if debug:
        print(gettimestr(), api, data)
        if rsp != None:
            for dataKey in rsp:
                if dataKey == "content":
                    print("         ", dataKey, type(rsp[dataKey]), rsp[dataKey])
                    if type(rsp[dataKey]) == type({}):
                        for key1 in rsp[dataKey]:
                            print("                  ", key1, rsp[dataKey][key1])
                    if type(rsp[dataKey]) == type([]):
                        length = len(rsp[dataKey])
                        for i in range(length):
                            print("                  ", i, rsp[dataKey][i])
                else:
                    print("         ", dataKey, rsp[dataKey])
        else:
            print(rsp)
    return rsp
# print("sha256", ezhashlib.sha256(config.custodyPassOfCustodyadmin))
# print("sha256", ezhashlib.sha256('abc123'))
# exit()
def run_bot():
    global userInfo, twiToken
    mail = config.mailOfCustodyadmin
    mailpass = config.mailpassOfCustodyadmin
    isAdmin = config.isAdminOfCustodyadmin
    gasecret = config.gasecretUATOfCustodyadmin

    custodyAccount = config.custodyAccountOfCustodyadmin
    custodyPass = config.custodyPassOfCustodyadmin

    custodyUrl = config.custodyUrlUAT

    try:
        print("GA:", getGACode(gasecret))
        t0 = time.time()
        loginOk = False
        userInfo = {}
        print(gettimestr(), "start...")
        if custodyLoginGet2FA(custodyUrl, custodyAccount, custodyPass, isAdmin):
            t2 = time.time()
            for i in range(20):
                print("try "+str(i)+" time")
                time.sleep(10)
                code = get2FACode(mail, mailpass, int(t2), True)
                if code == '':
                    continue
                else:
                    print("2FA:", code)
                    if custodyLoginBy2FA(custodyUrl, custodyAccount, code):
                        print("login succcess")
                        loginOk = True
                        break
                    else:
                        print("login fail")
        # userInfo["userId"] = 66
        print("userInfo:", userInfo)
        if isAdmin == False:
        # if True:
            if loginOk:
                rsp = custodyApiCall(custodyUrl, "user/queryInfo", { "userId": userInfo["userId"] }, True)
                rsp = custodyApiCall(custodyUrl, "user/queryUserLastSubmitTime", {"userId": userInfo["userId"]}, True)
                rsp = custodyApiCall(custodyUrl, "user/getDepositAddress", {"userId": userInfo["userId"], "tokenId": 17}, True)
                rsp = custodyApiCall(custodyUrl, "transaction/queryTransactionByUser", {
                        "userId": userInfo["userId"],
                        "pageSize": 10000,
                        "pageNum": 1,
                        "txTypes": [
                            1,
                            2,
                            3
                        ]
                    }, True)
                rsp = custodyApiCall(custodyUrl, "user/queryNft", {
                        "userId": userInfo["userId"],
                        "pageSize": 200,
                        "pageNum": 1
                    }, True)
                rsp = custodyApiCall(custodyUrl, "token/getTokenList", {"userId": userInfo["userId"], "loginUserId": userInfo["userId"]}, True)
                rsp = custodyApiCall(custodyUrl, "user/getDepositAddress", {"userId": userInfo["userId"], "tokenId": 9}, True)
                rsp = custodyApiCall(custodyUrl, "token/getNftList", {}, True)
                while True:
                    rsp = custodyApiCall(custodyUrl, "user/queryBalance", {"userId": userInfo["userId"]}, True)
                    for i in range(len(rsp["content"])):
                        print("                  ", rsp["content"][i]['name'], rsp["content"][i]['balance'])
                    # rsp = custodyApiCall(custodyUrl, "user/queryStakingBalance", {"userId": userInfo["userId"]}, True)
                    # rsp = custodyApiCall(custodyUrl, "user/queryUnStakingBalance", {"userId": userInfo["userId"]}, True)
                    # rsp = custodyApiCall(custodyUrl, "transaction/queryStaking", {
                    #     "userId": userInfo["userId"],
                    #     "pageNum": 1,
                    #     "pageSize": 10,
                    #     "status": 10,
                    #     "tokenId": 17,
                    # }, True)
                    # rsp = custodyApiCall(custodyUrl, "transaction/queryStaking", {
                    #     "userId": userInfo["userId"],
                    #     "pageNum": 1,
                    #     "pageSize": 10,
                    #     "status": 11,
                    #     "tokenId": 17,
                    # }, True)
                    # rsp = custodyApiCall(custodyUrl, "transaction/queryStaking", {
                    #     "userId": userInfo["userId"],
                    #     "pageNum": 1,
                    #     "pageSize": 10,
                    #     "status": 12,
                    #     "tokenId": 17,
                    # }, True)
                    # rsp = custodyApiCall(custodyUrl, "transaction/queryUnStaking", {
                    #     "userId": userInfo["userId"],
                    #     "pageNum": 1,
                    #     "pageSize": 10,
                    #     "status": 10,
                    #     "tokenId": 17,
                    # }, True)
                    # rsp = custodyApiCall(custodyUrl, "transaction/queryUnStaking", {
                    #     "userId": userInfo["userId"],
                    #     "pageNum": 1,
                    #     "pageSize": 10,
                    #     "status": 11,
                    #     "tokenId": 17,
                    # }, True)
                    # rsp = custodyApiCall(custodyUrl, "transaction/queryUnStaking", {
                    #     "userId": userInfo["userId"],
                    #     "pageNum": 1,
                    #     "pageSize": 10,
                    #     "status": 12,
                    #     "tokenId": 17,
                    # }, True)
                    time.sleep(10)
        if isAdmin == True:
        # if True:
            if loginOk:
                #while True:
                    rsp = custodyApiCall(custodyUrl, "user/queryInfo", { "userId": userInfo["userId"] }, True)
                    time.sleep(10)

        print(gettimestr(), "use time:", time.time() - t0)
    except Exception as e1:
        traceback.print_exc()

