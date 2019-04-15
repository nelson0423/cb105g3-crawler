"""
Google Search
"""
from crawler import logger, random_requests_get, path_config
from bs4 import BeautifulSoup
from urllib.parse import unquote, quote
import warnings
import os
from selenium.webdriver import Chrome
import time
from urllib.request import urlretrieve
import random

warnings.filterwarnings("ignore")


def process(keyword, prefix, collect_cnt):
    driver = Chrome("../chromedriver")
    driver.set_window_rect(10, 10, 1027, 768)
    img_dir = path_config["crawler"] + "/images"
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    keyword = quote(keyword)
    logger.debug("keyword: {}, collect_cnt{}".format(keyword, collect_cnt))
    ret = list()
    url_pattern = "https://www.google.com/search?q={}&source=lnms&tbm=isch&sa=X&ved=0ahUKEwi33-bootHhAhVXyIsBHXN5CAMQ_AUIDigB&biw=1920&bih=979"
    url = url_pattern.format(keyword)
    driver.get(url)
    _len = 0
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # 處理延遲載入機制(JavaScript模擬滑鼠滾輪下滾)
        time.sleep(3)  # 2秒有時會來不及, 所以改用3秒
        hSRGPd = driver.find_elements_by_css_selector("a[jsname='hSRGPd']")
        logger.info("已載入{}筆資料".format(len(hSRGPd)))
        if _len == len(hSRGPd):
            break
        _len = len(hSRGPd)  # 筆數一樣表示沒有意見了
    g_urls = []
    for d in hSRGPd:
        g_url = d.get_attribute("href")
        g_urls.append(g_url)
    delay = [1, 2, 3, 1.5, 2.3, 3.2]
    for i in range(len(g_urls)):
        try:
            g_url = g_urls[i]
            # print("g_url=", g_url)
            driver.get(g_url)
            time.sleep(random.choice(delay))
            img_url = driver.find_element_by_css_selector("img[class='irc_mi'][src^='http']").get_attribute("src")
            print("img_url=", img_url)
            fpath = img_dir + "/" + prefix + format(i, "03d") + "." + img_url.split(".")[-1]
            urlretrieve(img_url, fpath)
            if i > collect_cnt:
                break
        except Exception as e:
            print("Error: {}".format(e))
    return ret


if __name__ == '__main__':
    items = ["豬尾巴", "避雷帽", "吊籃"]
    for item in items:
        keyword = "露營+" + item
        prefix = item + "_"
        process(keyword, prefix, 200)
