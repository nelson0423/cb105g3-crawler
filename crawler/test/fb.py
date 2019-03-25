"""
facebook
"""
from crawler import gmail
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
    driver.find_element_by_id("email").send_keys(gmail["addr"])
    driver.find_element_by_id("pass").send_keys(gmail["pwd"])
    driver.execute_script("console.log('send email/pass done ...');")
    driver.find_element_by_xpath("//input[@data-testid='royal_login_button']").click()  # 登入button的id會動態產生, 所以改用xpath
    time.sleep(1)


# 粉專: 山林鳥日子
def process_30birds():
    login()
    url = "https://www.facebook.com/30birdz/"
    url_reviews = url + "reviews/"
    driver.get(url_reviews)
    time.sleep(1)
    _len = 0
    while True:
        # 處理延遲載入機制
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # 2秒有時會來不及
        # reviews = [reviews.find_element_by_tag_name("p") for reviews in
        #            driver.find_elements_by_xpath("//div[@class='_5pbx userContent _3576']")]
        reviews = driver.find_elements_by_xpath("//div[@class='_5pbx userContent _3576']")
        print("已載入", len(reviews), "筆意見")
        if _len == len(reviews):
            break
        _len = len(reviews)  # 筆數一樣表示沒有意見了
    for review in reviews:
        print("id: {}, comment: {}".format(review.get_attribute("id"), review.find_element_by_tag_name("p").text))


# 社團: 頭家愛露營
def process_Toujiafamilycamping():
    login()
    url = "https://www.facebook.com/groups/476415489178482/"


if __name__ == '__main__':
    process_30birds()  # 粉專: 山林鳥日子
    # process_Toujiafamilycamping()  # 社團: 頭家愛露營
