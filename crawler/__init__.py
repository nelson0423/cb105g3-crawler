import logging
import logging.config
import pandas as pd
import os
import json
import csv
import requests
import time
import random

log_dir = "/logs/crawler/"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_config.ini')
logging.config.fileConfig(log_file_path)
logger = logging.getLogger("crawler")

gmail = {"addr": "iiicb105g3@gmail.com", "pwd": "cb105g3-III"}
db_config = {
    "mongodb": "mongodb://35.201.196.175:27017/",
    # "mongodb": "mongodb://localhost:27017/",
    "mysql": {
        # "host": "35.229.201.139",
        "host": "localhost",
        "port": 3306,
        "database": "camp_db",
        # "user": "iii",
        "user": "root",
        # "password": "Qwer_0987"
        "password": "root123",
        # "db": "camp_db",
        # "passwd": "root123",
        # "charset": "utf8"
    }
}
path_config = {
    "crawler": "/temp/crawler"
}


def stop_watch(value):
    valueD = (((value / 365) / 24) / 60)
    days = int(valueD)
    valueH = (valueD - days) * 365
    hours = int(valueH)
    valueM = (valueH - hours) * 24
    minutes = int(valueM)
    valueS = (valueM - minutes) * 60
    seconds = int(valueS)
    logging.info("Days: {}, Hours: {}, Minutes: {}, Seconds: {}".format(days, hours, minutes, seconds))


def json_to_csv(json_data, file_path):
    """
    JSON轉成CSV
    """
    pdir = os.path.dirname(file_path)
    if not os.path.exists(pdir):
        os.makedirs(pdir)
    pd.DataFrame(json_data).to_csv(file_path, header=True, index=False, quoting=csv.QUOTE_ALL, encoding="utf-8")


def csv_to_json(file_path):
    """
    CSV轉成JSON
    """
    df = pd.read_csv(file_path, encoding="utf-8")

    def trans_if_json(data):
        try:
            return eval(data)
        except:
            return data

    for col in df.columns:
        df[col] = df[col].apply(trans_if_json)
    return json.loads(df.to_json(orient="records"))


user_agents = ["Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20130406 Firefox/23.0", \
               "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0", \
               "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533+ \
               (KHTML, like Gecko) Element Browser 5.0", \
               "IBM WebExplorer /v0.94', 'Galaxy/1.0 [en] (Mac OS X 10.5.6; U; en)", \
               "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)", \
               "Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14", \
               "Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) \
                Version/6.0 Mobile/10A5355d Safari/8536.25", \
               "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) \
                Chrome/28.0.1468.0 Safari/537.36", \
               "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; TheWorld)"]
proxy_list = [
    "http://211.23.149.28:80",
    "http://211.23.149.29:80",
    "http://122.116.67.146:60730"
]
delays = [10, 12, 13, 14, 15, 16, 17, 18, 19]
random_urls = [
    "http://www.u-car.com.tw/",
    "http://www.piaa.com.tw/",
    "https://my.garmin.com.tw/",
    "http://www.appledaily.com.tw/",
    "https://www.rakuten.co.jp/shop/"
]


def random_requests_get(url):
    headers = {
        "user-agent": random.choice(user_agents),
        "referrer": "https://google.com",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Pragma": "no-cache"
    }
    proxies = {
        "http": random.choice(proxy_list)
    }
    requests.get(random.choice(random_urls))
    time.sleep(random.choice(delays))
    # response = requests.get(url, headers=headers, proxies=proxies)
    response = requests.get(url)
    return response


# __all__ = ["logging"]

if __name__ == '__main__':
    logger.debug("Log中文測試 abc 123")
    # logger.debug(os.path.abspath(__file__))
    # logger.debug(os.path.dirname(os.path.abspath(__file__)))
    # logger.debug(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_config.ini'))
