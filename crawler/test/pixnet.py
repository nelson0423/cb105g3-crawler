"""
痞客邦
"""

import requests
from bs4 import BeautifulSoup
import warnings

warnings.filterwarnings("ignore")


def process(url):
    response = requests.get(url)
    response.encoding = "utf-8"  # 解決亂碼問題
    html = BeautifulSoup(response.text)
    # print(html)
    # content = html.find("div", {"id": "article-content-inner"})
    content = html.select_one("div#article-content-inner")
    # contents = content.find_all("span")
    contents = content.select("span")
    text_content = "\n".join([str(c.text) for c in contents if hasattr(c, "text")])  # isinstance(c.next, str)
    print(text_content)


if __name__ == '__main__':
    url = "http://may0708.pixnet.net/blog/post/435497693-%E3%80%90%E6%98%B5%E6%98%B5%E5%AA%BD%E9%9C%B2%E7%87%9F%E8%B6%A3%E3%80%91%E8%8B%97%E6%A0%97%E5%A4%A7%E6%B9%96_%E5%B2%B8%E4%B9%8B%E6%BA%AA%E4%BC%91%E9%96%92%E6%9C%83%E9%A4%A8"
    process(url)
