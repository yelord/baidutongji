# --*-- coding:utf-8 ---*---
#
#    Author: Yelord
#    Email:  yelord@qq.com
#
# Created by yelord on 2017/3/19.
# 由百度官方php demo 转 python
#
import json
import requests
import math
import StringIO, gzip
import rsa
import uuid

LOGIN_URL = 'https://api.baidu.com/sem/common/HolmesLoginService'
API_URL = 'https://api.baidu.com/json/tongji/v1/ReportService'
UUID = str(uuid.uuid1())  # 'parkoutlets'
ACCOUNT_TYPE = '1'  # ZhanZhang:1,FengChao:2,Union:3,Columbus:4


def encrypt(data):
    # load公钥和密钥
    with open('api_pub.key') as publickfile:
        p = publickfile.read()
        pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(p)

    # 用公钥加密
    n = int(math.ceil(len(data) * 1.0 / 117))
    ret = ''
    for i in range(n):
        gzdata = data[i * 117:(i + 1) * 117]
        ret += rsa.encrypt(gzdata, pubkey)

    # print ret
    return ret


# 解压gzip
def gzdecode(data):
    f = StringIO.StringIO(data)
    gziper = gzip.GzipFile(fileobj=f, compresslevel=9)
    data2 = gziper.read()  # 读取解压缩后数据
    gziper.close()
    return data2


# 压缩gzip
def gzencode(data):
    f = StringIO.StringIO()
    gziper = gzip.GzipFile(fileobj=f, mode='wb', compresslevel=9, )
    gziper.write(data)  # 压缩后数据
    gziper.close()
    return f.getvalue()


class BaiduTongji(object):
    ucid = None
    st = None

    def __init__(self, username, password, token):
        self.username = username
        self.password = password
        self.token = token

        # login
        # self.prelogin()
        ret = self.dologin()
        self.ucid = str(ret['ucid'])
        self.st = ret['st']

    def prelogin(self):
        data = {'username': self.username,
                'token': self.token,
                'functionName': 'preLogin',
                'uuid': UUID,
                'request': {'osVersion': 'windows', 'deviceType': 'pc', 'clientVersion': '1.0'},
                }

        headers = {'UUID': UUID, 'account_type': ACCOUNT_TYPE,
                   'Content-Type': 'data/gzencode and rsa public encrypt;charset=UTF-8'
                   }

        # 压缩
        post_data = gzencode(json.dumps(data))
        # 加密
        post_data = encrypt(post_data)

        resp = requests.post(LOGIN_URL, data=post_data, headers=headers)
        ret = json.loads(gzdecode(resp.content[8:]))
        print 'prelogin:', ret

    def dologin(self):
        data = {'username': self.username,
                'token': self.token,
                'functionName': 'doLogin',
                'uuid': UUID,
                'request': {'password': self.password}
                }

        headers = {'UUID': UUID, 'account_type': ACCOUNT_TYPE,
                   'Content-Type': 'data/gzencode and rsa public encrypt;charset=UTF-8'
                   }

        # 压缩
        post_data = gzencode(json.dumps(data))
        # 加密
        post_data = encrypt(post_data)
        # post
        resp = requests.post(LOGIN_URL, data=post_data, headers=headers)
        ret = json.loads(gzdecode(resp.content[8:]))
        if ret['retcode'] == 0:
            print u'dologin:', ret['retmsg']
            print ret['ucid']
            print ret['st']
        return ret

    def dologout(self):
        data = {'username': self.username,
                'token': self.token,
                'functionName': 'doLogout',
                'uuid': UUID,
                'request': {'ucid': self.ucid, 'st': self.st, }
                }

        headers = {'UUID': UUID, 'account_type': ACCOUNT_TYPE,
                   'Content-Type': 'data/gzencode and rsa public encrypt;charset=UTF-8'
                   }

        # 压缩
        post_data = gzencode(json.dumps(data))
        # 加密
        post_data = encrypt(post_data)
        # post
        resp = requests.post(LOGIN_URL, data=post_data, headers=headers)
        ret = json.loads(gzdecode(resp.content[8:]))
        print 'logout:', ret['retmsg']

    def getsitelist(self):
        url = API_URL + '/getSiteList'
        headers = {'UUID': UUID, 'USERID': self.ucid, 'Content-Type': 'data/json;charset=UTF-8'}
        data = {'header': {'username': self.username, 'password': self.st, 'token': self.token,
                           'account_type': ACCOUNT_TYPE, },
                'body': None, }
        post_data = json.dumps(data)
        resp = requests.post(url, data=post_data, headers=headers)
        # print resp.json()
        return resp.json()['body']['data'][0]['list']

    def getdata(self, para):
        url = API_URL + '/getData'
        headers = {'UUID': UUID, 'USERID': self.ucid, 'Content-Type': 'data/json;charset=UTF-8'}
        data = {'header': {'username': self.username, 'password': self.st, 'token': self.token,
                           'account_type': ACCOUNT_TYPE, },
                'body': para, }

        post_data = json.dumps(data)
        resp = requests.post(url, data=post_data, headers=headers)
        # print resp.json()
        return resp.json()['body']



'''
        # 地域分布报告 visit/district/a    pv_count (浏览量(PV))
                                        # pv_ratio (浏览量占比，%)
                                        # visit_count (访问次数)
                                        # visitor_count (访客数(UV))
                                        # new_visitor_count (新访客数)
                                        # new_visitor_ratio (新访客比率，%)
                                        # ip_count (IP 数)
                                        # bounce_ratio (跳出率，%)
                                        # avg_visit_time (平均访问时长，秒)
                                        # avg_visit_pages (平均访问页数)
                                        # trans_count (转化次数)
                                        # trans_ratio (转化率，%)
        # 网站概况 overview/getTimeTrendRpt (趋势数据)  单选：
                                        # pv_count (浏览量(PV))
                                        # visitor_count (访客数(UV))
                                        # ip_count (IP 数)
                                        # bounce_ratio (跳出率，%)
                                        # avg_visit_time (平均访问时长，秒)
        # 趋势分析 trend/time/a    pv_count (浏览量(PV))
                                        # pv_ratio (浏览量占比，%)
                                        # visit_count (访问次数)
                                        # visitor_count (访客数(UV))
                                        # new_visitor_count (新访客数)
                                        # new_visitor_ratio (新访客比率，%)
                                        # ip_count (IP 数)
                                        # bounce_ratio (跳出率，%)
                                        # avg_visit_time (平均访问时长，秒)
                                        # avg_visit_pages (平均访问页数)
                                        # trans_count (转化次数)
                                        # trans_ratio (转化率，%)
                                        # avg_trans_cost (平均转化成本，元)
                                        # income (收益，元)
                                        # profit (利润，元)
                                        # roi (投资回报率，%)

'''
if __name__ == '__main__':
    # 配置自己的用户/密码/token
    bdtj = BaiduTongji('your-user-name','your-password','your-token')

    sites = bdtj.getsitelist()
    for item in sites:
        print item['domain'], item['site_id']

    site_id = sites[0]['site_id']

    # para = {'site_id': site_id,  # 站点ID
    #         'method': 'trend/time/a',  # 趋势分析报告
    #         'start_date': '20170316',  # 所查询数据的起始日期
    #         'end_date': '20170320',  # 所查询数据的结束日期
    #         'metrics': 'pv_count,visitor_count',  # 所查询指标为PV和UV
    #         'max_results': '0',  # 返回所有条数
    #         'gran': 'day',  # 按天粒度  day/hour/week/month
    #         }

    para = {'site_id': site_id,  # 站点ID
            'method': 'trend/time/a',  # 趋势分析报告
            'start_date': '20170321',  # 所查询数据的起始日期
            'end_date': '20170321',  # 所查询数据的结束日期
            'metrics': 'pv_count,visitor_count, avg_visit_time',  # 所查询指标为PV和UV
            'max_results': '0',  # 返回所有条数
            'gran': 'hour',  # 粒度
            }

    ret = bdtj.getdata(para)
    print json.dumps(ret['data'][0]['result']['items'], indent=4)

    # bdtj.dologout()
