# -*- coding: utf-8 -*-
"""
@Date: Created on Fri Dec  7 09:12:19 2018
@Author: Haojun Gao
@Description: 爬马蜂窝地区景点（北京）的名录，但是不包括爬景点内部的景点，例如午门。
"""

import os
import json
from random import choice
from proxy import prepare_proxy
from urllib import request, parse
from proxy_github import getProxy


def get_last_line(input_file):
    file_size = os.path.getsize(input_file)
    block_size = 1024
    dat_file = open(input_file, 'rb')
    last_line = ""
    if file_size > block_size:
        max_seek_point = (file_size // block_size)
        dat_file.seek((max_seek_point - 1) * block_size)
    elif file_size:
        dat_file.seek(0, 0)
    lines = dat_file.readlines()
    if lines:
        last_line = lines[-1].strip()
    dat_file.close()
    return last_line


def header_useragent():
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Host': 'www.mafengwo.cn',
        'Origin': 'http://www.mafengwo.cn',
        'Referer': 'http://www.mafengwo.cn/mdd/map/10065.html',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }

    userAgent = [
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko",
        "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
        "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
        "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)"]
    return headers, userAgent


if __name__ == "__main__":
    post_url = "http://www.mafengwo.cn/mdd/base/map/getPoiList"
    # ip_list = prepare_proxy()
    ip_list = getProxy()
    print("[Get_List]The valid IP: ", ip_list)

    page = 1

    filePath = "./data/list_all.txt"
    if os.access(filePath, os.F_OK):
        print("[Get_List]Given file path is exist.")
        page_byte = get_last_line(filePath).split()[-1]
        # 检查是否只有表头
        if page_byte.decode(encoding='utf-8') != "page":
            page = int(page_byte.decode(encoding='utf-8'))
            print("[Get_List]Already spider page :", page)
    else:
        with open(filePath, 'a+', encoding='utf-8') as f:
            f.write("name\ttype_id\tid\tlat\tlng\tpage\n")

    with open(filePath, 'a+', encoding='utf-8') as f:
        while 1:
            param = {'mddid': '10065', 'page': page}
            param = parse.urlencode(param)
            param = param.encode('utf-8')
            # headers = {'User-Agent':ua.random}
            headers, userAgent = header_useragent()
            headers['User-Agent'] = choice(userAgent)
            req = request.Request(post_url, param, headers=headers)
            proxy_handler = request.ProxyHandler(choice(ip_list))
            opener = request.build_opener(proxy_handler)
            try:
                response = opener.open(req)
            except:
                print("[Get_List]False to spider page " + str(page))
                page -= 1
                ip_list = prepare_proxy()
            else:
                print("[Get_List]Success to spider page " + str(page))
                # 返回的是一个json格式的字符串，将字符串转为dict对象
                data_json = json.loads(response.read().decode("utf8"))
                list_all = data_json.get("list")
                # 判断是否爬完
                if len(list_all) == 0:
                    break
                for loc in list_all:
                    loc["name"].replace(' ', '')
                    f.write(str(loc["name"]) + "\t" + str(loc["type_id"]) + "\t" +
                            str(loc["id"]) + "\t" + str(loc["lat"]) + "\t" +
                            str(loc["lng"]) + "\t" + str(page) + "\n")
            page += 1
        print("[Get_List]Done spider all the list")
