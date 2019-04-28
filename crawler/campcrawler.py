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
import os
# import MySQLdb
import mysql.connector
from urllib.request import urlretrieve

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
            text_content = text_content.replace("\xa0", " ")
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

    def extract_evshhips(self):
        data_list = list()
        url = "https://evshhips.pixnet.net/blog/category/4337992"
        response = requests.get(url)
        response.encoding = "utf-8"  # 解決亂碼問題
        html = BeautifulSoup(response.text)
        mylink = html.select_one("#mylink")

        def get_data_by_url(url):
            data = dict()
            for d in data_list:
                if url == d.get("url"):
                    data = d
                    break
            return data

        for type in mylink.select("div.inner-box"):
            if type.select_one("img"):
                # logger.debug(type)
                style = type.select_one("h6").text.strip().split(" ")[0]
                url_list = type.select("a")
                for u in url_list:
                    title = u.text
                    url = u["href"]
                    logger.debug("style: {}, title: {}, url: {}".format(style, title, url))
                    content = self.extract_pixnet(url)["text_content"]
                    data = get_data_by_url(url)
                    if not data.get("url"):
                        data["style"] = list()
                        data["title"] = title
                        data["url"] = url
                        data["content"] = content
                        data_list.append(data)
                    data["style"].append(style)
        return data_list

    def evshhips_to_mongodb(self, json_data, drop):
        conn = None
        try:
            conn = MongoClient(db_config["mongodb"])
            db = conn.test
            coll = db.evshhips
            if drop:
                coll.drop()
            for doc in json_data:
                coll.update({"style": doc["style"], "title": doc["title"], "url": doc["url"]}, doc, upsert=True)
        except Exception as e:
            logger.error("Error:", e)
        finally:
            if conn:
                conn.close()
                logger.debug("connection closed ...")

    def get_camp_style_dict(self):
        style_dict = dict()
        mydict_base_dir = "./mydict"
        f_prefix = "camp_style_"
        for dir_path, dir_names, file_names in os.walk(mydict_base_dir):
            for single_file in file_names:
                if single_file.startswith(f_prefix):
                    with open(os.path.join(dir_path, single_file), "r", encoding="utf-8") as f:
                        f_content = f.read()
                    key = single_file.replace(f_prefix, "").split(".")[0].split("_")[1]
                    value = f_content.split("\n")
                    style_dict[key] = value
        return style_dict

    def merge_rvcamp_and_pixnet(self, rvcamp_json, pixnet_json):
        ret = list()
        logger.debug("rvcamp_json.keys: {}".format(rvcamp_json[0].keys()))
        logger.debug("pixnet_json.keys: {}".format(pixnet_json[0].keys()))
        style_dict = self.get_camp_style_dict()
        for rvcamp in rvcamp_json:
            style = None
            tmp = 0
            tags = list()
            for pixnet in pixnet_json:
                if rvcamp["camp_title"] == pixnet["camp_title"]:
                    content = pixnet["content"]
                    if content:
                        for k, v in style_dict.items():
                            matches = 0
                            for w in v:
                                cnt = content.count(w)
                                matches += cnt
                                if cnt > 0 and tags.count(w) == 0:
                                    tags.append(w)
                            if matches > tmp:
                                tmp = matches
                                style = k
                    break
            if style:
                rvcamp["style"] = style
                rvcamp["tags"] = " ".join(tags)
                ret.append(rvcamp)
        return ret

    def camplist_to_mongodb(self, json_data, drop):
        conn = None
        try:
            conn = MongoClient(db_config["mongodb"])
            db = conn.test
            coll = db.camplist
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

    def camplist_to_mysql(self, json_data):
        conn = None
        try:
            # conn = MySQLdb.connect(**db_config["mysql"])
            conn = mysql.connector.connect(**db_config["mysql"])
            # conn.autocommit(False)
            cur = conn.cursor()
            sql = "delete from camp_webs"
            res = cur.execute(sql)
            logger.debug("sql: {}, res: {}".format(sql, res))
            sql = "delete from camp_tels"
            res = cur.execute(sql)
            logger.debug("sql: {}, res: {}".format(sql, res))
            sql = "delete from camp_features"
            res = cur.execute(sql)
            logger.debug("sql: {}, res: {}".format(sql, res))
            sql = "delete from camp_list"
            res = cur.execute(sql)
            logger.debug("sql: {}, res: {}".format(sql, res))
            ins_datas = []
            for data in json_data:
                ins_data = (
                    data["camp_title"], data["camp_site"], data["addr"], (data["latlong"] if data["latlong"] else "NA"),
                    data["location"],
                    data["style"], data["tags"])
                ins_datas.append(ins_data)
            sql = ("insert into camp_list ( \n"
                   + "camp_title, camp_site, addr, latlong, location, style, tags \n"
                   + ") values ( \n"
                   + "%s, %s, %s, %s, %s, %s, %s \n"
                   + ")")
            res = cur.executemany(sql, ins_datas)
            logger.debug("sql: {}, res: {}".format(sql, res))
            feature_datas = []
            tel_datas = []
            web_datas = []
            for data in json_data:
                camp_title = data["camp_title"]
                for feature in data["features"]:
                    feature_datas.append((camp_title, feature))
                for tel in data["tel"]:
                    if tel == "" or tel_datas.count((camp_title, tel)) != 0:
                        print(">>>> ", tel)
                        continue
                    tel_datas.append((camp_title, tel))
                for ws in data["web_site"]:
                    for item in ws.items():
                        web_datas.append((camp_title, item[0], item[1]))
            sql = ("insert into camp_features ( \n"
                   + "camp_title, feature \n"
                   + ") values ( \n"
                   + "%s, %s \n"
                   + ")")
            res = cur.executemany(sql, feature_datas)
            logger.debug("sql: {}, res: {}".format(sql, res))
            sql = ("insert into camp_tels ( \n"
                   + "camp_title, tel \n"
                   + ") values ( \n"
                   + "%s, %s \n"
                   + ")")
            res = cur.executemany(sql, tel_datas)
            logger.debug("sql: {}, res: {}".format(sql, res))
            sql = ("insert into camp_webs ( \n"
                  + "camp_title, name, url \n"
                  + ") values ( \n"
                  + "%s, %s, %s \n"
                  + ")")
            res = cur.executemany(sql, web_datas)
            logger.debug("sql: {}, res: {}".format(sql, res))
            conn.commit()
        except Exception as e:
            logger.error("Error: {}".format(e.with_traceback()))
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
                logger.debug("conn.close() ...")

    def extract_google_images(self, keyword, prefix, collect_cnt, img_dir):
        driver = Chrome("./chromedriver")
        driver.set_window_rect(10, 10, 1027, 768)
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
        keyword = quote(keyword)
        logger.debug("keyword: {}, collect_cnt{}".format(keyword, collect_cnt))
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
                driver.get(g_url)
                time.sleep(random.choice(delay))
                img_url = driver.find_element_by_css_selector("img[class='irc_mi'][src^='http']").get_attribute("src")
                logger.debug("img_url: {}".format(img_url))
                fpath = img_dir + "/" + prefix + format(i, "03d") + "." + img_url.split(".")[-1]
                urlretrieve(img_url, fpath)
                if i > collect_cnt:
                    break
            except Exception as e:
                logger.error("Error: {}".format(e))


if __name__ == '__main__':
    cc = CampCrawler()

    rvcamp_file_path = path_config["crawler"] + "/rvcamp.csv"
    pixnet_file_path = path_config["crawler"] + "/pixnet.csv"
    fb_file_path = path_config["crawler"] + "/fb.csv"
    evshhips_file_path = path_config["crawler"] + "/evshhips.csv"
    camplist_file_path = path_config["crawler"] + "/camplist.csv"
    """
    爬露營窩轉到csv和mongodb
    """
    # rvcamp_json = cc.extract_rvcamp(-1) # -1表示全抓
    # cc.rvcamp_to_mongodb(rvcamp_json, True)
    # json_to_csv(rvcamp_json, rvcamp_file_path)
    """
    將露營窩csv轉成json
    """
    # rvcamp_json = csv_to_json(rvcamp_file_path)
    # rvcamp_json = rvcamp_json[:10]
    """
    將露營窩json, 用google search方式查出痞客邦網址, 並爬出資料寫入mongodb
    """
    # pixnet_json = cc.google_search_extract_pixnet_blog(rvcamp_json)
    # cc.pixnet_to_mongodb(pixnet_json, True)
    # json_to_csv(pixnet_json, pixnet_file_path)
    """
    將露營窩所記錄的fb粉專, 爬出評論並寫入mongodb
    """
    # fb_json = cc.extract_fb_comment(rvcamp_json)
    # cc.fb_to_mongodb(fb_json, True)
    # json_to_csv(fb_json, fb_file_path)
    """
    將何師夫痞客邦懶人包, 爬出部落格並寫入mongodb
    """
    # evshhips_json = cc.extract_evshhips()
    # cc.evshhips_to_mongodb(evshhips_json, True)
    # json_to_csv(evshhips_json, evshhips_file_path)
    """
    將露營窩(營地基本資料)與痞客邦(文章轉換成營地風格)的資料合併
    """
    # rvcamp_json = csv_to_json(rvcamp_file_path)
    # pixnet_json = csv_to_json(pixnet_file_path)
    # camplist_json = cc.merge_rvcamp_and_pixnet(rvcamp_json, pixnet_json)
    # cc.camplist_to_mongodb(camplist_json, True)
    # json_to_csv(camplist_json, camplist_file_path)
    """
    將camplist寫入MySQL
    """
    # camplist_json = csv_to_json(camplist_file_path)
    # cc.camplist_to_mysql(camplist_json)
    """
    將爬出指定搜尋的google圖片
    """
    # items = ["豬尾巴", "避雷帽", "吊籃"]
    # for item in items:
    #     keyword = "露營+" + item
    #     prefix = item + "_"
    #     cc.extract_google_images(keyword, prefix, 200, path_config["crawler"] + "/images/" + item)

    """
    all csv to mongodb
    """
    rvcamp_json = csv_to_json(rvcamp_file_path)
    cc.rvcamp_to_mongodb(rvcamp_json, True)

    pixnet_json = csv_to_json(pixnet_file_path)
    cc.pixnet_to_mongodb(pixnet_json, True)

    fb_json = csv_to_json(fb_file_path)
    cc.fb_to_mongodb(fb_json, True)

    camplist_json = csv_to_json(camplist_file_path)
    cc.camplist_to_mongodb(camplist_json, True)
