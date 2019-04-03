from crawler import stop_watch, logger, gmail, path_config, db_config, json_to_csv, csv_to_json, random_requests_get
import requests
from bs4 import BeautifulSoup
import warnings
import time
from pymongo import MongoClient
from urllib.parse import unquote, quote
import pandas as pd
import random
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

warnings.filterwarnings("ignore")


class CampCrawler(object):

    def __init__(self):
        self.__config = {
            "url_rvcamp": "https://rvcamp.org/"
        }

    def extract_rvcamp(self, limit_count):
        total = []
        response = requests.get(self.__config["url_rvcamp"])
        html = BeautifulSoup(response.text)
        menus = html.select_one("#home-menu").select("li > a")
        cnt_area = 0
        bk = False
        extract_count = 0
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
                        extract_count += 1
                        cnt_campsite = cnt_campsite + 1
                        row = dict()
                        # row["_id"] = "campsite_" + format(cnt_area, "02d") + "_" + format(cnt_campsite, "04d")
                        row["location"] = menu.text
                        campsite_url = campsite["href"]
                        try:
                            logger.debug("content_url: {}".format(campsite_url))
                            response = requests.get(campsite_url)
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
                            self.__merge_rvcamp_text1(text1, row)
                        except Exception as e:
                            logger.error("Error: {}, campsite_url: {}".format(e, campsite_url))
                        logger.info("row: {}".format(row));
                        total.append(row)
                        # if False and cnt_area == 1 and cnt_campsite == 10:  # 限制爬的數量(False則不限制數量)
                        if extract_count == limit_count:
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
        return total  # json array

    def __merge_rvcamp_text1(self, datas, row):
        keymap = dict((("電話", "tel"), ("地址", "addr"), ("名稱", "camp_site"), ("網站", "web_site"), ("座標", "latlong")))
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

    def rvcamp_to_mongodb(self, json_data, drop):
        conn = None
        try:
            conn = MongoClient(db_config["mongodb"])
            db = conn.test
            coll = db.rvcamp
            if drop:
                coll.drop()
            for doc in json_data:
                coll.update({"camp_title": doc["camp_title"]}, doc, upsert=True)
        except Exception as e:
            logger.error("Error:", e)
        finally:
            if conn:
                conn.close()
                logger.debug("connection closed ...")

    def extract_pixnet(self, url):
        ret = dict()
        ret["text_content"] = ""
        try:
            response = requests.get(url)
            response.encoding = "utf-8"  # 解決亂碼問題
            html = BeautifulSoup(response.text)
            # logger.debug(html)
            article_content = html.select_one("div#article-content-inner")
            # text_content = self.__get_text_content(article_content.select("*"))
            text_content = "\n".join(c.strip() for c in article_content.text.split("\n") if "" != c.strip())
            ret["text_content"] = text_content
            # logger.info(ret["text_content"])
        except Exception as e:
            logger.error("Error: {}".format(e))
            ret["text_content"] = "{}".format(e)
        return ret

    def __get_text_content(self, elements):
        contents = []
        for ele in elements:
            content = ele.find(text=True, recursive=False)
            if content and "" != content.strip():
                contents.append(content.strip())
        return "\n".join(contents)

    def pixnet_to_mongodb(self, json_data, drop):
        conn = None
        try:
            conn = MongoClient(db_config["mongodb"])
            db = conn.test
            coll = db.pixnet
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

    def google_search_extract_pixnet_blog(self, camp_list):
        datas = list()

        def search_filter(url_list):
            for u in url_list:
                if u.find("pixnet.net/blog/post/") != -1: yield u

        delays = [9, 10, 5]
        for idx in range(len(camp_list)):
            if idx % random.choice(delays) == 0:
                time.sleep(30)
            camp = camp_list[idx]
            camp_title = camp["camp_title"]
            camp_site = camp["camp_site"]
            logger.info("idx: {}, camp_site: {}, camp_title: {}".format(idx, camp_site, camp_title))
            collect_cnt = 1
            max_start = 30
            # search_result = self.google_search("\"露營\"+\"痞客邦\"+\"" + camp_site + "\"", search_filter, collect_cnt,
            #                                    max_start)
            search_result = self.google_search("露營+痞客邦+" + camp_site, search_filter, collect_cnt,
                                               max_start)
            logger.debug("search_result: {}".format(search_result))
            for url in search_result:
                content = self.extract_pixnet(url)["text_content"]
                data = dict()
                data["camp_site"] = camp_site
                data["camp_title"] = camp_title
                data["pixnet_url"] = url
                data["content"] = content  # .replace("\"", "")
                datas.append(data)
        return datas

    def google_search(self, keyword, search_filter, collect_cnt, max_start):
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
                ret.extend(search_filter(url_list))
                if len(ret) == 0:
                    break
                ret = ret[: collect_cnt] if len(ret) > collect_cnt else ret
                logger.debug("len(ret): {}".format(len(ret)))
                if len(ret) == collect_cnt:
                    break
            except Exception as e:
                logger.error("Error: {}, url: {}".format(e, url))
        return ret

    def init_fb(self):
        url_entry = "https://www.facebook.com/"
        chrome_options = Options()
        chrome_options.add_experimental_option('prefs',
                                               {
                                                   'profile.default_content_setting_values.notifications': 1})  # 允許通知(1) 封鎖通知(2)
        driver = Chrome("chromedriver", chrome_options=chrome_options)
        driver.set_window_rect(10, 10, 1027, 768)
        driver.get(url_entry)
        # 進行登入
        driver.find_element_by_css_selector("#email").send_keys(gmail["addr"])
        driver.find_element_by_css_selector("#pass").send_keys(gmail["pwd"])
        # driver.execute_script("console.log('send email/pass done ...');")
        driver.find_element_by_css_selector(
            "input[data-testid='royal_login_button']").click()  # 登入button的id會動態產生, 改用attribute
        time.sleep(1)
        return driver

    def extract_fb_comment(self, camp_list):
        datas = list()
        for camp in camp_list:
            web_site = camp["web_site"]
            fb_url = ""
            for web in web_site:
                for v in web.values():
                    if v.find("facebook.com") != -1:
                        fb_url = v
                    if "" != fb_url:
                        break
                if "" != fb_url:
                    break
            if "" != fb_url:
                data = dict()
                data["camp_site"] = camp["camp_site"]
                data["camp_title"] = camp["camp_title"]
                data["fb_url"] = fb_url
                datas.append(data)
        driver = self.init_fb()
        delays = [7, 3, 5, 2, 4]
        for data in datas:
            try:
                url = data["fb_url"]
                url_reviews = url + "reviews/"
                logger.debug("url_reviews: {}".format(url_reviews))
                driver.get(url_reviews)
                time.sleep(random.choice(delays))
                _len = 0
                while True:
                    driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);")  # 處理延遲載入機制(JavaScript模擬滑鼠滾輪下滾)
                    time.sleep(3)
                    reviews = driver.find_elements_by_css_selector("div[class='_5pbx userContent _3576']")
                    logger.info("已載入{}筆意見".format(len(reviews)))
                    if _len == len(reviews):
                        break
                    _len = len(reviews)  # 筆數一樣表示沒有意見了
                comments = list()
                for review in reviews:
                    # logger.info(
                    #     "id: {}, comment: {}".format(review.get_attribute("id"),
                    #                                  review.find_element_by_tag_name("p").text))
                    comment = review.find_element_by_tag_name("p").text
                    if comment and "" != comment.strip():
                        comments.append(comment.strip())
                data["comments"] = comments
            except Exception as e:
                logger.error("Error: {}".format(e))
        return datas

    def fb_to_mongodb(self, json_data, drop):
        conn = None
        try:
            conn = MongoClient(db_config["mongodb"])
            db = conn.test
            coll = db.facebook
            if drop:
                coll.drop()
            for doc in json_data:
                coll.update({"camp_title": doc["camp_title"], "fb_url": doc["fb_url"]}, doc, upsert=True)
        except Exception as e:
            logger.error("Error:", e)
        finally:
            if conn:
                conn.close()
                logger.debug("connection closed ...")


if __name__ == '__main__':
    cc = CampCrawler()

    rvcamp_file_path = path_config["crawler"] + "/rvcamp.csv"
    pixnet_file_path = path_config["crawler"] + "/pixnet.csv"
    fb_file_path = path_config["crawler"] + "/fb.csv"
    """
    爬露營窩轉到csv和mongodb
    """
    # rvcamp_json = cc.extract_rvcamp(-1) # -1表示全抓
    # cc.rvcamp_to_mongodb(rvcamp_json, True)
    # json_to_csv(rvcamp_json, rvcamp_file_path)
    """
    將露營窩csv轉成json
    """
    rvcamp_json = csv_to_json(rvcamp_file_path)
    # rvcamp_json = rvcamp_json[:10]
    """
    將露營窩json, 用google search方式查出痞客邦網址, 並爬出資料寫入mongodb
    """
    pixnet_json = cc.google_search_extract_pixnet_blog(rvcamp_json)
    cc.pixnet_to_mongodb(pixnet_json, True)
    json_to_csv(pixnet_json, pixnet_file_path)
    """
    將露營窩所記錄的fb粉專, 爬出評論並寫入mongodb
    """
    fb_json = cc.extract_fb_comment(rvcamp_json)
    # logger.debug(fb_json)
    cc.fb_to_mongodb(fb_json, True)
    json_to_csv(fb_json, fb_file_path)
