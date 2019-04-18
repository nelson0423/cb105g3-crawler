from urllib.request import quote, urlopen, Request
from bs4 import BeautifulSoup
import json

url = "https://www.amazon.com/product-reviews/B01MG0733A/ref=cm_cr_getr_d_paging_btm_prev_1?_encoding=UTF8&showViewpoints=1&pageNumber=1"
req = Request(url)
req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36")
response = urlopen(req)
html = BeautifulSoup(response)
# print(html)

customer_reviews = html.find_all("div", {"class": "a-section celwidget"})
# print(len(customer_reviews))

for cr in customer_reviews:
    # print(cr)
    review_body = cr.find("span", {"data-hook": "review-body"})
    print("".join([str(t) for t in review_body.next.contents]).replace("<br/>", "\n"))
    print("-----------------------------------------------------------------------------------------------------------")
