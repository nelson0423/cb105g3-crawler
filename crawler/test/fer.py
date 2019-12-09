"""
Foreign Exchange Rates
"""
from crawler import logger
import requests
from bs4 import BeautifulSoup
import warnings
import calendar
import pandas as pd

warnings.filterwarnings("ignore")


def process(url):
    response = requests.get(url)
    response.encoding = "utf-8"  # 解決亂碼問題
    html = BeautifulSoup(response.text)
    # logger.debug(html)
    fer = html.select_one("table[title^='Foreign Exchange Rates']")
    # print(fer)
    currMonth = fer.select_one("thead > tr > th:nth-child(3)").text.strip()
    print("currMonth = {}".format(currMonth))
    currMonthAry = [data for data in currMonth.split(" ") if data != ""][::-1]
    currMonthAry[1] = format({v: k for k, v in enumerate(calendar.month_name)}[currMonthAry[1]], "02d")
    currMonthStr = "-".join(currMonthAry)
    print("currMonthStr = {}".format(currMonthStr))
    countryList = [ele.text.strip() for ele in fer.select("tbody > tr > th[class!='subhead1']")]
    print("len = {}, countryList = {}".format(len(countryList), countryList))
    currencyList = [ele.text.strip() for ele in fer.select("tbody > tr > td:nth-child(2)")]
    print("len = {}, currencyList = {}".format(len(currencyList), currencyList))
    erList = [ele.text.strip() for ele in fer.select("tbody > tr > td:nth-child(3)")]
    print("len = {}, erList = {}".format(len(erList), erList))
    df = pd.DataFrame(list(zip(countryList, currencyList, erList)),
                      columns=["country", "currency", "exchange_rate"])
    print(df)
    df.to_csv("D:/Users/nelson_chou/Desktop/FER_" + currMonthStr + ".csv", sep=",", encoding="utf-8")


if __name__ == '__main__':
    url = "https://www.federalreserve.gov/releases/g5/current/"
    process(url)
