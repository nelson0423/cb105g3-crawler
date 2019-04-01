"""
Google Search
"""
from crawler import logger, random_requests_get
from bs4 import BeautifulSoup
from urllib.parse import unquote, quote
import warnings

warnings.filterwarnings("ignore")


def process(keyword, search_filter, collect_cnt, max_start):
    """
    :param keyword: 搜尋關鍵字
    :param search_filter: 過濾器實作(generator)
    :param collect_cnt: 需蒐集的筆數
    :param max_start: 最大分頁總筆數
    :return: 搜尋到的網址陣列
    """
    keyword = quote(keyword)
    logger.debug("keyword: {}, collect_cnt{}, max_start: {}".format(keyword, collect_cnt, max_start))
    ret = list()
    url_pattern = "https://www.google.com/search?q={}&start={}"

    for start in range(0, max_start, 10):
        url = url_pattern.format(keyword, start)
        try:
            logger.debug("url: {}".format(url))
            response = random_requests_get(url)
            html = BeautifulSoup(response.text)
            url_list = [unquote(d["href"], "utf-8").replace("/url?q=", "").split("&sa=")[0] for d in
                        html.select("h3.r > a")]  # 該頁搜尋結果連結
            if len(url_list) == 0:
                break
            ret.extend(search_filter(url_list))
            ret = ret[0: collect_cnt] if len(ret) > collect_cnt else ret
            if len(ret) == collect_cnt:
                break
        except Exception as e:
            logger.error("Error: {}, url: {}".format(e, url))
    return ret


if __name__ == '__main__':
    keyword = "\"露營\"+\"pixnet\"+\"朱比特咖啡\""


    def search_filter(url_list):
        for u in url_list:
            if u.find("pixnet.net/blog") != -1: yield u


    collect_cnt = 3
    max_start = 30
    result = process(keyword, search_filter, collect_cnt, max_start)
    logger.debug("result: {}".format(result))
