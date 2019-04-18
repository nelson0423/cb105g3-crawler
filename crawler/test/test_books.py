from urllib.request import quote, urlopen, Request
from bs4 import BeautifulSoup
import json

url = "https://www.books.com.tw/web/sys_botm/outdoors/073402?loc=P_0002_2_002"
req = Request(url)
req.add_header("User-Agent", "Mozilla/5.0")
response = urlopen(req)
html = BeautifulSoup(response)
# print(html)

covers = html.find("ul", {"class": "cntli_001 cntli_001a clearfix"}).find_all("li")
print(len(covers))

for cover in covers:
    # print(cover)
    if cover.find("h4") is not None:
        print(cover.find("h4").find("a").text)
        print(cover.find("span", {"class": "price"}).find("b").text)
        print("-----------------------------------------------------------------------------------------------------------")
