"""
何師傅
"""
import requests
from bs4 import BeautifulSoup
import warnings

warnings.filterwarnings("ignore")


def process():
    url = "https://evshhips.pixnet.net/blog/category/4337992"
    response = requests.get(url)
    response.encoding = "utf-8"  # 解決亂碼問題
    html = BeautifulSoup(response.text)
    mylink = html.select_one("#mylink")
    for type in mylink.select("div.inner-box"):
        if type.select_one("img"):
            print(type)
            style = type.select_one("h6").text.strip().split(" ")[0]
            print("style: {}".format(style))
            url_list = type.select("a")
            for u in url_list:
                title = u.text
                url = u["href"]
                print("title: {}, url: {}".format(title, url))
            print("----------------")


if __name__ == '__main__':
    process()
