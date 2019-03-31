"""
痞客邦
"""
from crawler import logger
import requests
from bs4 import BeautifulSoup
import warnings

warnings.filterwarnings("ignore")


def process(url):
    ret = dict()
    response = requests.get(url)
    response.encoding = "utf-8"  # 解決亂碼問題
    html = BeautifulSoup(response.text)
    # logger.debug(html)
    article_content = html.select_one("div#article-content-inner")
    span_contents = article_content.select("span")
    # text_content = "\n".join([str(c.find(text=True, recursive=False)) for c in contents if hasattr(c, "text")])
    contents = list()
    for c in span_contents:
        content = c.find(text=True, recursive=False)
        if content and "" != content.strip():
            contents.append(content.strip())
    ret["text_content"] = "\n".join(contents)
    # logger.info(ret["text_content"])
    return ret


if __name__ == '__main__':
    # url = "http://may0708.pixnet.net/blog/post/435497693-%E3%80%90%E6%98%B5%E6%98%B5%E5%AA%BD%E9%9C%B2%E7%87%9F%E8%B6%A3%E3%80%91%E8%8B%97%E6%A0%97%E5%A4%A7%E6%B9%96_%E5%B2%B8%E4%B9%8B%E6%BA%AA%E4%BC%91%E9%96%92%E6%9C%83%E9%A4%A8"
    url = "http://happymommy.pixnet.net/blog/post/112628743-%E2%99%A5%E9%9B%99%E5%AF%B6%E9%9C%B2%E7%87%9F%E8%B6%A3%E3%80%82%E7%B5%82%E6%96%BC%E9%A6%96%E9%9C%B2-%E5%85%8D%E8%B2%BB%E7%9A%84%E5%85%A7%E6%B9%96%E7%A2%A7%E5%B1%B1%E9%9C%B2"
    process(url)
