from selenium.webdriver import Chrome
import time
import warnings
import requests
from bs4 import BeautifulSoup
from pytube import *
import os
import crawler


warnings.filterwarnings("ignore")

driver = Chrome("./chromedriver")
driver.get("https://www.youtube.com/view_all_playlists")
driver.find_element_by_id("identifierId").send_keys("nelson0423@gmail.com")
driver.find_element_by_id("identifierNext").click()
time.sleep(3)
driver.find_element_by_class_name("whsOnd").send_keys(crawler.p)
driver.find_element_by_id("passwordNext").click()
time.sleep(15)
cookies_list = driver.get_cookies()

s = requests.Session()
for cookie in cookies_list:
    s.cookies.set(cookie["name"], cookie["value"])
response = s.get("https://www.youtube.com/view_all_playlists")
html = BeautifulSoup(response.text)
playlists = html.find_all("li", class_="playlist-item")
urllist = []
crawler_url = ""
for l in playlists:
    title = l.find("a", "vm-video-title-text").text
    url = "https://www.youtube.com" + l.find("a", "vm-video-title-text")["href"]
    urllist.append({"title": title, "url": url})
    if "crawler" == title:
        crawler_url = url
print("urllist:", urllist)
print("crawler_url:", crawler_url)

#pl = Playlist(crawler_url, suppress_exception=True)
pl = Playlist("https://www.youtube.com/watch?v=iSkRGgYSQfY&list=PLOHZClinoCW7K_eX6MpKDUFc2Fmw0GvzJ", suppress_exception=True)
dir_path = "D:/temp/youtube/"
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
pl.download_all(dir_path)
print(pl.parse_links())
print("DONE ...")