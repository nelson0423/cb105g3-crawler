from urllib.request import quote, urlopen
import json

keyword = "帳篷"
# by: 篩選
# newest: 分頁
url = "https://shopee.tw/api/v2/search_items/?by=relevancy&keyword=" + quote(
    keyword) + "&limit=50&newest=0&order=desc&page_type=search"
print("搜尋:", url)
response = urlopen(url)
search = json.load(response)
items = search["items"]
for item in items:
    print("itemid:", item["itemid"])
    print("shopid:", item["shopid"])
    print("name:", item["name"])
    url = "https://shopee.tw/api/v2/item/get?itemid=" + str(item["itemid"]) + "&shopid=" + str(item["shopid"])
    print("商品:", url)
    response = urlopen(url)
    jo = json.load(response)
    product = jo["item"]
    # print("description:", product["description"])
    print("rating_star:", product["item_rating"]["rating_star"])
    models = product["models"]
    print("models:")
    for model in models:
        print(" - modelid:", model["modelid"], ",", "name:", model["name"], ",", "price:", model["price"] / 100000, ","
              , "sold:", str(model["sold"]), ",", "stock:", str(model["stock"]))
    images = product["images"]
    print("images:")
    for imageid in images:
        print(" - image:", "https://cf.shopee.tw/file/" + imageid)
    url = "https://shopee.tw/api/v2/shop/get?is_brief=1&shopid=" + str(item["shopid"])
    print("賣家:", url)
    response = response = urlopen(url)
    jo = json.load(response)["data"]
    account = jo["account"]
    print("name:", jo["name"])
    print("rating_star:", jo["rating_star"])
    print("userid", jo["userid"])
    print("username:", account["username"])
    print("total_avg_star:", account["total_avg_star"])
    print("vacation", jo["vacation"])
    print("---------------------------------------------------------------------------")
