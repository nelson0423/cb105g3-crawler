"""
露營窩
Ref: CSS Selector
"""

from crawler import stop_watch, path_config
import requests
from bs4 import BeautifulSoup
import warnings
import time
import pandas as pd
import os

warnings.filterwarnings("ignore")


def merge_text1(datas, row):
    keymap = dict((("電話", "tel"), ("地址", "addr"), ("X網站", "web_site"), ("座標", "latlong")))
    for data in datas:
        title = keymap.get(data[0].text)
        if title is None:
            # print("title is None:", data[0].text)
            continue
        content = data[1]
        if "tel" == title:
            content = [d.text for d in content.select("span[itemprop='telephone']")]
        elif "web_site" == title:
            content = [{d.text: d["href"]} for d in content.select("a")]
        elif "latlong" == title:
            if content.select_one("#gps_10") is not None:
                content = content.select_one("#gps_10").text.split("\xa0")
            else:
                content = "N/A"
        else:
            content = content.text
        row[title] = content


def process(url):
    total = []
    start = time.time()
    # print("start:", start)
    response = requests.get(url)
    html = BeautifulSoup(response.text)
    menus = html.select_one("#home-menu").select("li > a")
    cnt_area = 0
    bk = False
    for menu in menus:
        cnt_area = cnt_area + 1
        cnt_campsite = 0
        murl = menu["href"]
        print("區域:", menu.text, "----------------------------")
        # print("murl:", murl)
        response = requests.get(murl)
        html = BeautifulSoup(response.text)
        nav = html.select_one("div.nav-links")  # 分頁導覽區域
        if nav is not None:
            last_page_num = int(
                nav.select_one("a.page-numbers:nth-last-of-type(2)")["href"].split("/")[-1])  # 倒數第2個才是最後一頁
            print("總共", last_page_num, "頁")
            for num in range(last_page_num):
                pnum = str(num + 1)
                print(menu.text, "第", pnum, "頁", "----------------------------")
                page_url = murl + "/page/" + pnum
                # print("page_url:", page_url)
                response = requests.get(page_url)
                html = BeautifulSoup(response.text)
                campsites = html.select("h2.entry-title-list > a")
                for campsite in campsites:
                    cnt_campsite = cnt_campsite + 1
                    row = dict()
                    row["_id"] = "campsite_" + format(cnt_area, "02d") + "_" + format(cnt_campsite, "04d")
                    row["location"] = menu.text
                    campsite_url = campsite["href"]
                    process_content(campsite_url, row)
                    print("row:", row)
                    total.append(row)
                    if cnt_area == 1 and cnt_campsite == 10:
                        bk = True
                    if bk:
                        break
                # <<< end of page campsite for loop
                if bk:
                    break
            # <<< end of location page for loop
            if bk:
                break
        # <<< end of location menu for loop
    print("cnt_campsite:", cnt_campsite)
    end = time.time()
    # print("end:", end)
    stop_watch(end - start)
    return total


def process_content(content_url, row):
    try:
        # print("content_url:", content_url)
        response = requests.get(content_url)
        html = BeautifulSoup(response.text)
        print("entry-title: {}".format(html.select_one("h1.entry-title").text))
        row["camp_site_name"] = html.select_one("h1.entry-title").text
        text0 = [t.select_one("a").text for t in
                 html.select_one("#text0").select(
                     "div[class^='t-camp-']"  # 為t-camp-開頭
                     + ":not([class$='-none'])"  # 不為-none結尾
                     + ":not([class='t-camp-area'])"  # 不為t-camp-area
                 )
                 ]
        # print("\ttext0: {}".format(text0))
        row["features"] = text0
        text1 = [t.select("span[class^=t-]") for t in html.select_one("#text1").select("li")]
        merge_text1(text1, row)
    except Exception as e:
        print("Error: {}, content_url: {}".format(e, content_url))


def json_to_csv(json_data, file_path):
    import csv
    pdir = os.path.dirname(file_path)
    if not os.path.exists(pdir):
        os.makedirs(pdir)
    pd.DataFrame(json_data).to_csv(file_path, header=True, index=False, quoting=csv.QUOTE_ALL)


def json_to_mongodb():
    pass


def csv_to_mongodb(file_path):
    pass


if __name__ == '__main__':
    url = "https://rvcamp.org/"
    json_data = process(url)
    file_path = path_config["crawler"] + "/rvcamp.csv"
    json_to_csv(json_data, file_path)
