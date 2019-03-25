"""
露營窩
"""

from crawler import stop_watch
import requests
from bs4 import BeautifulSoup
import warnings
import time

warnings.filterwarnings("ignore")


def extracttext1(datas):
    ret = dict()
    for data in datas:
        title = data[0].text
        content = data[1]
        if "電話" == title:
            content = [d.text for d in content.select("span[itemprop=telephone]")]
        elif "網站" == title:
            content = [{d.text: d["href"]} for d in content.select("a")]
        elif "座標" == title:
            if content.select_one("#gps_10") is not None:
                content = content.select_one("#gps_10").text.split("\xa0")
            else:
                content = "N/A"
        else:
            content = content.text
        ret[title] = content
    return ret


def process(url):
    total = []
    start = time.time()
    # print("start:", start)
    response = requests.get(url)
    html = BeautifulSoup(response.text)
    menus = html.select_one("#home-menu").select("li > a")
    cnt_area = 0
    cnt_campsite = 0
    for menu in menus:
        cnt_area = cnt_area + 1
        murl = menu["href"]
        print("區域:", menu.text, "----------------------------")
        # print("murl:", murl)
        response = requests.get(murl)
        html = BeautifulSoup(response.text)
        nav = html.select_one("div.nav-links")  # 分頁導覽區域
        if nav is not None:
            last_page_num = int(nav.select("a.page-numbers")[-2]["href"].split("/")[-1])  # 倒數第2個才是最後一頁
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
                    row = dict()
                    row["loc"] = menu.text
                    cnt_campsite = cnt_campsite + 1
                    campsite_url = campsite["href"]
                    process_content(campsite_url, row)
                    # print(row)
                    # total.append(row)
    print("cnt_campsite:", cnt_campsite)
    end = time.time()
    # print("end:", end)
    stop_watch(end - start)


def process_content(content_url, row):
    try:
        # print("content_url:", content_url)
        response = requests.get(content_url)
        html = BeautifulSoup(response.text)
        print(">>> entry-title: {}".format(html.select_one("h1.entry-title").text))
        row["entry-title"] = html.select_one("h1.entry-title").text
        # print(html.select_one("#text0").select("div[class^='t-camp-']:not([class$='-none'])"))
        text0 = [dict([(t["class"][0], t.select_one("a").text)]) for t in
                 html.select_one("#text0").select("div[class^='t-camp-']:not([class$='-none'])")]
        # text0 = [t.select_one("a").text for t in
        #          html.select_one("#text0").select("div[class^='t-camp-']:not([class$='-none'])")]
        print("\ttext0: {}".format(text0))
        row["text0"] = text0
        text1 = [t.select("span[class^=t-]") for t in html.select_one("#text1").select("li")]
        text1 = extracttext1(text1)
        print("\ttext1: {}".format(text1))
        row["text1"] = text1
    except Exception as e:
        print("Error: {}, content_url: {}".format(e, content_url))


if __name__ == '__main__':
    url = "https://rvcamp.org/"
    process(url)
