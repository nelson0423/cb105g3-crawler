"""
露營窩
Ref: CSS Selector
"""

from crawler import stop_watch, logger, path_config, db_config, json_to_csv, csv_to_json
import requests
from bs4 import BeautifulSoup
import warnings
import time
from pymongo import MongoClient
import pandas as pd

warnings.filterwarnings("ignore")


def merge_text1(datas, row):
    keymap = dict((("電話", "tel"), ("地址", "addr"), ("名稱", "camp_site"), ("X網站", "web_site"), ("座標", "latlong")))
    for data in datas:
        title = keymap.get(data[0].text)
        if title is None:
            logger.debug("title is None: {}".format(data[0].text))
            continue
        content = data[1]
        if "tel" == title:
            content = [d.text for d in content.select("span[itemprop='telephone']")]
        elif "web_site" == title:
            content = [{d.text: d["href"]} for d in content.select("a")]
        elif "latlong" == title:
            if content.select_one("#gps_10") is not None:
                content = ",".join(content.select_one("#gps_10").text.split("\xa0"))
            else:
                content = "N/A"
        else:
            content = content.text
        row[title] = content


def process(url):
    """
    將爬蟲內容轉成JSON
    """
    total = []
    response = requests.get(url)
    html = BeautifulSoup(response.text)
    menus = html.select_one("#home-menu").select("li > a")
    cnt_area = 0
    bk = False
    for menu in menus:
        cnt_area = cnt_area + 1
        cnt_campsite = 0
        murl = menu["href"]
        logger.info("區域: {} ----------------------------".format(menu.text))
        logger.debug("murl: {}".format(murl))
        response = requests.get(murl)
        html = BeautifulSoup(response.text)
        nav = html.select_one("div.nav-links")  # 分頁導覽區域
        if nav is not None:
            last_page_num = int(
                nav.select_one("a.page-numbers:nth-last-of-type(2)")["href"].split("/")[-1])  # 倒數第2個才是最後一頁
            logger.info("總共{}頁".format(last_page_num))
            for num in range(last_page_num):
                pnum = str(num + 1)
                logger.info("{} - 第{}頁 ----------------------------".format(menu.text, pnum))
                page_url = murl + "/page/" + pnum
                logger.debug("page_url: {}".format(page_url))
                response = requests.get(page_url)
                html = BeautifulSoup(response.text)
                campsites = html.select("h2.entry-title-list > a")
                for campsite in campsites:
                    cnt_campsite = cnt_campsite + 1
                    row = dict()
                    # row["_id"] = "campsite_" + format(cnt_area, "02d") + "_" + format(cnt_campsite, "04d")
                    row["location"] = menu.text
                    campsite_url = campsite["href"]
                    process_content(campsite_url, row)
                    logger.info("row: {}".format(row));
                    total.append(row)
                    if False and cnt_area == 1 and cnt_campsite == 3:  # 限制爬的數量(False則不限制數量)
                        bk = True  # Python沒有label, 所以用這種鳥方式
                    if bk:
                        break
                # <<< end of page campsite for loop
                if bk:
                    break
            # <<< end of location page for loop
        if bk:
            break
    # <<< end of location menu for loop
    logger.info("total count: {}".format(len(total)))
    return total


def process_content(content_url, row):
    try:
        logger.debug("content_url: {}".format(content_url))
        response = requests.get(content_url)
        html = BeautifulSoup(response.text)
        logger.info("entry-title: {}".format(html.select_one("h1.entry-title").text))
        row["camp_title"] = html.select_one("h1.entry-title").text
        text0 = [t.select_one("a").text for t in
                 html.select_one("#text0").select(
                     "div[class^='t-camp-']"  # 為t-camp-開頭
                     + ":not([class$='-none'])"  # 不為-none結尾
                     + ":not([class='t-camp-area'])"  # 不為t-camp-area
                 )
                 ]
        row["features"] = text0
        text1 = [t.select("span[class^=t-]") for t in html.select_one("#text1").select("li")]
        merge_text1(text1, row)
    except Exception as e:
        logger.error("Error: {}, content_url: {}".format(e, content_url))


def json_to_mongodb_rvcamp(json_data, drop):
    """
    JSON寫入MongoDB
    """
    # import json
    # from bson import json_util
    conn = None
    try:
        conn = MongoClient(db_config["mongodb"])
        db = conn.test
        coll = db.camp_list
        if drop:
            coll.drop()
        for doc in json_data:
            # doc = json.loads(json.dumps(doc, default=json_util.default))  # trans dict in list to json -> 多此一舉
            # fdoc = coll.find_one({"camp_title": doc["camp_title"]})
            coll.update({"camp_title": doc["camp_title"]}, doc, upsert=True)
    except Exception as e:
        logger.error("Error:", e)
    finally:
        if conn:
            conn.close()
            logger.debug("connection closed ...")


def json_to_mongodb_pixnet(json_data, drop):
    """
    JSON寫入MongoDB
    """
    # import json
    # from bson import json_util
    conn = None
    try:
        conn = MongoClient(db_config["mongodb"])
        db = conn.test
        coll = db.blog_pixnet
        if drop:
            coll.drop()
        for doc in json_data:
            coll.update({"camp_title": doc["camp_title"], "pixnet_url": doc["pixnet_url"]}, doc, upsert=True)
    except Exception as e:
        logger.error("Error:", e)
    finally:
        if conn:
            conn.close()
            logger.debug("connection closed ...")


def csv_to_mongodb_rvcamp(file_path, drop):
    """
    CSV寫入MongoDB
    """
    json_data = csv_to_json(file_path)
    json_to_mongodb_rvcamp(json_data, drop)


def proces_pixnet_blog(camp_list):
    """
    依JSON找出營地的痞客邦部落格
    :param camp_list: 營地資訊JSON
    :return:
    """
    datas = list()
    import crawler.test.google_search as google_search
    import crawler.test.pixnet as pixnet
    def search_filter(url_list):
        for u in url_list:
            if u.find("pixnet.net/blog") != -1: yield u

    for idx in range(len(camp_list)):
        camp = camp_list[idx]
        camp_title = camp["camp_title"]
        camp_site = camp["camp_site"]
        logger.info("idx: {}, camp_site: {}, camp_title: {}".format(idx, camp_site, camp_title))
        collect_cnt = 3
        max_start = 50
        search_result = google_search.process("露營+" + camp_site, search_filter, collect_cnt, max_start)
        logger.debug("search_result: {}".format(search_result))
        for url in search_result:
            content = pixnet.process(url)["text_content"]
            data = dict()
            data["camp_site"] = camp_site
            data["camp_title"] = camp_title
            data["pixnet_url"] = url
            data["content"] = content  # .replace("\"", "")
            datas.append(data)
    return datas


def main():
    start = time.time()
    json_data_rvcamp = process("https://rvcamp.org/")
    json_data_pixnet = proces_pixnet_blog(json_data_rvcamp)
    json_to_mongodb_rvcamp(json_data_rvcamp, True)
    json_to_mongodb_pixnet(json_data_pixnet, True)
    end = time.time()
    stop_watch(end - start)


if __name__ == '__main__':
    main()

    file_path = path_config["crawler"] + "/rvcamp.csv"

    """
    將爬蟲內容轉成JSON
    """
    # logger.info(">>> 將爬蟲內容轉成JSON - Start")
    # url = "https://rvcamp.org/"
    # json_data = process(url)
    # logger.info(">>> 將爬蟲內容轉成JSON - End")

    """
    JSON轉成CSV
    """
    # logger.info(">>> JSON轉成CSV - Start")
    # json_to_csv(json_data, file_path)
    # logger.info(">>> JSON轉成CSV - End")

    """
    JSON寫入MongoDB
    """
    # logger.info(">>> JSON寫入MongoDB - Start")
    # json_to_mongodb_rvcamp(json_data, False)
    # logger.info(">>> JSON寫入MongoDB - End")

    """
    CSV轉成JSON
    """
    # logger.info(">>> CSV轉成JSON - Start")
    # d = csv_to_json(file_path)
    # # print("### ", d[0]["features"], type(d[0]["features"]))
    # logger.info(">>> CSV轉成JSON - End")

    """
    CSV寫入MongoDB
    """
    # logger.info(">>> CSV寫入MongoDB - Start")
    # csv_to_mongodb_rvcamp(file_path, True)
    # logger.info(">>> CSV寫入MongoDB - End")
