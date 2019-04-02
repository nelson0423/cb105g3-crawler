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
    ret["text_content"] = ""
    try:
        response = requests.get(url)
        response.encoding = "utf-8"  # 解決亂碼問題
        html = BeautifulSoup(response.text)
        # logger.debug(html)
        article_content = html.select_one("div#article-content-inner")
        text_content = get_text_content(article_content.select("*"))
        # print("\n".join(c.strip() for c in article_content.text.split("\n") if "" != c.strip()))
        # span_contents = article_content.select("span")
        # text_content = "\n".join([str(c.find(text=True, recursive=False)) for c in contents if hasattr(c, "text")])
        # text_content = get_text_content(span_contents)
        # if "" == text_content:
        #     p_contents = article_content.select("p")
        #     text_content = get_text_content(p_contents)
        ret["text_content"] = text_content
        # logger.info(ret["text_content"])
    except Exception as e:
        logger.error("Error: {}".format(e))
        ret["text_content"] = "{}".format(e)
    return ret


def get_text_content(elements):
    ret = ""
    contents = []
    for ele in elements:
        content = ele.find(text=True, recursive=False)
        if content and "" != content.strip():
            contents.append(content.strip())
    return "\n".join(contents)


if __name__ == '__main__':
    # url = "http://may0708.pixnet.net/blog/post/435497693-%E3%80%90%E6%98%B5%E6%98%B5%E5%AA%BD%E9%9C%B2%E7%87%9F%E8%B6%A3%E3%80%91%E8%8B%97%E6%A0%97%E5%A4%A7%E6%B9%96_%E5%B2%B8%E4%B9%8B%E6%BA%AA%E4%BC%91%E9%96%92%E6%9C%83%E9%A4%A8"
    url = "http://yuanbar2618.pixnet.net/blog/post/195881067-20171230-20180101%E6%88%91%E6%84%9B%E9%9C%B2%E7%87%9F-%E5%8F%B0%E5%8C%97%E8%8F%AF%E4%B8%AD%E9%9C%B2%E7%87%9F%E5%A0%B4-%E8%80%81%E7%9A%AE"
    process(url)
