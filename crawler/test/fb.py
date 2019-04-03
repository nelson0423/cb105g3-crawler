"""
facebook
Ref: CSS Selector
"""
from crawler import gmail, logger
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import time

url_entry = "https://www.facebook.com/"
chrome_options = Options()
chrome_options.add_experimental_option('prefs',
                                       {'profile.default_content_setting_values.notifications': 1})  # 允許通知(1) 封鎖通知(2)
driver = Chrome("../chromedriver", chrome_options=chrome_options)
driver.set_window_rect(10, 10, 1027, 768)
driver.get(url_entry)


def login():
    driver.find_element_by_css_selector("#email").send_keys(gmail["addr"])
    driver.find_element_by_css_selector("#pass").send_keys(gmail["pwd"])
    # driver.execute_script("console.log('send email/pass done ...');")
    driver.find_element_by_css_selector(
        "input[data-testid='royal_login_button']").click()  # 登入button的id會動態產生, 改用attribute
    time.sleep(1)


# 粉專: 山林鳥日子
def process_30birds():
    login()
    urls = ["https://www.facebook.com/微笑山丘-223226418074079/", "https://www.facebook.com/30birdz/"]
    for url in urls:
        url_reviews = url + "reviews/"
        driver.get(url_reviews)
        time.sleep(1)
        _len = 0
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # 處理延遲載入機制(JavaScript模擬滑鼠滾輪下滾)
            time.sleep(3)  # 2秒有時會來不及, 所以改用3秒
            reviews = driver.find_elements_by_css_selector("div[class='_5pbx userContent _3576']")
            logger.info("已載入{}筆意見".format(len(reviews)))
            if _len == len(reviews):
                break
            _len = len(reviews)  # 筆數一樣表示沒有意見了
        for review in reviews:
            logger.info("id: {}, comment: {}".format(review.get_attribute("id"), review.find_element_by_tag_name("p").text))


# 社團: 頭家愛露營
def process_Toujiafamilycamping():
    login()
    url = "https://www.facebook.com/groups/476415489178482/"


if __name__ == '__main__':
    process_30birds()  # 粉專: 山林鳥日子
    # process_Toujiafamilycamping()  # 社團: 頭家愛露營
