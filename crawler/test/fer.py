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
    response = requests.get(url)
    response.encoding = "utf-8"  # 解決亂碼問題
    html = BeautifulSoup(response.text)
    # logger.debug(html)
    fer = html.select_one("table[title^='Foreign Exchange Rates']")
    # print(fer)
    currMonth = fer.select("thead > tr > th")[2].text.strip()
    print("### currMonth = {}".format(currMonth))
    countryEleList = fer.select("tbody > tr > th[class!='subhead1']")
    countryList = [countryEleList[i].text.strip() for i in range(len(countryEleList))]
    print("len = {}, countryList = {}".format(len(countryList), countryList))
    currencyEleList = fer.select("tbody > tr > td:nth-child(2)")
    currencyList = [currencyEleList[i].text.strip() for i in range(len(currencyEleList))]
    print("len = {}, currencyList = {}".format(len(currencyList), currencyList))
    erEleList = fer.select("tbody > tr > td:nth-child(3)")
    erList = [erEleList[i].text.strip() for i in range(len(erEleList))]
    print("len = {}, erList = {}".format(len(erList), erList))
    return ret


if __name__ == '__main__':
    url = "https://www.federalreserve.gov/releases/g5/current/"
    process(url)
