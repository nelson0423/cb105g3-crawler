from urllib.request import quote, urlopen, Request
import json

keyword = "帳篷"
url = "https://ecshweb.pchome.com.tw/search/v3.3/all/results?q=" + quote(keyword) + "&page=1&sort=sale/dc"
print("搜尋:", url)
req = Request(url)
req.add_header("User-Agent", "Mozilla/5.0")
response = urlopen(req)
search = json.load(response)
prods = search["prods"]
for prod in prods:
    print("Id:", prod["Id"])
    print("name:", prod["name"])
    url = "https://24h.pchome.com.tw/ecapi/ecshop/prodapi/v2/prod?id=" + prod["Id"] \
          + "&fields=Seq,Id,Name,Nick,Store,PreOrdDate,SpeOrdDate,Price,Discount,Pic,Weight,ISBN,Qty,Bonus,isBig,isSpec,isCombine,isDiy,isRecyclable,isCarrier,isMedical,isBigCart,isSnapUp,isDescAndIntroSync,isFoodContents,isHuge,isEnergySubsidy,isPrimeOnly,isPreOrder24h,isWarranty,isLegalStore"
    print("商品:", url)
    req = Request(url)
    req.add_header("User-Agent", "Mozilla/5.0")
    response = urlopen(req)
    jo = json.load(response)[prod["Id"] + "-000"]
    print("Price:", jo["Price"]["P"])
    print("picB:", "https://d.ecimg.tw" + jo["Pic"]["B"])
    print("---------------------------------------------------------------------------")
