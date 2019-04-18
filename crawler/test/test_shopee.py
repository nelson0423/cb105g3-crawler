from urllib.request import quote
from selenium.webdriver import Chrome
from bs4 import BeautifulSoup
import time


def get_bshtml_by_driver(driver, url, search_class, scroll_to_bottom):
    driver.implicitly_wait(10)  # seconds
    driver.get(url)
    driver.find_element_by_class_name(search_class)
    if scroll_to_bottom:
        for i in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/5*" + str(i + 1) + ");")
            time.sleep(0.2)
    return BeautifulSoup(driver.page_source)


keyword = "帳篷"
url = "https://shopee.tw/search?keyword=" + quote(keyword)
print("url:", url)

# 蝦皮無法直接請求
# warnings.filterwarnings("ignore")
# r = Request(url)
# r.add_header("user-agent", "Mozilla/5.0")
# response = urlopen(r)
# html = BeautifulSoup(response)
# print(html)

# 用chromedriver
driver = Chrome("./chromedriver.exe")
html = get_bshtml_by_driver(driver, url, "shopee-progress-bar", True)
# print(html)

items = html.find_all("div", class_="shopee-search-item-result__item")
# driver.quit()
print("len(items):", len(items))
for item in items:
    try:
        item_anchor = item.find("div").find("a")
        item_url = "https://shopee.tw" + item_anchor["href"]
        print(">>> 進入商品頁面:" + item_url)
        html = get_bshtml_by_driver(driver, item_url, "shopee-progress-bar", True)
        print(" - 商品名稱:", html.find("div", class_="qaNIZv").text)
        # 規格 VS 售價
        spec_price = driver.execute_script("_tmp = {};"
                                           + "var prods = document.getElementsByClassName('product-variation');"
                                           + "for(var i = 0, ii = prods.length; i < ii; ++i){"
                                           + "   prods[i].click();"
                                           + "   _tmp[prods[i].textContent] = document.getElementsByClassName('_3n5NQx')[0].innerHTML;"
                                           + "}"
                                           + "return _tmp;")
        if len(spec_price) != 0:
            for spec in spec_price:
                print(" - 規格:", spec, ", 售價:", spec_price[spec])
        else:
            # 無規格
            print(" - 售價:", html.find("div", class_="_3n5NQx").text)
    except TypeError as ve:
        print("[ERROR]", ve)
