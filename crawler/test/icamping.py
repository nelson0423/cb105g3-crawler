"""
愛露營
"""
from crawler import logger
import requests
import json


def process(url):
    response = requests.get(url)
    items = json.loads(response.text)["items"]
    logger.debug(items)
    limit_cnt = 3  # 限制帶出筆數(大於0才做限制)
    for idx in range(len(items)):
        item = items[idx]
        logger.info("{}.".format(idx + 1), item)
        logger.info("no: {}, store_id: {}, store_name: {}".format(idx + 1, item["store_id"], item["store_name"]))
        logger.info("address: {}, area: {}, city: {}".format(item["address"], item["area"], item["city"]))
        url = "https://icamping-prod.appspot.com/_ah/api/icamping_guest/v2/query_store_by_store_id?store_id=" + item[
            "store_id"]
        response = requests.get(url)
        content = json.loads(response.text)["items"][0]
        logger.info("description: {}".format(content["description"]))
        external_links = json.loads(content["external_links"])
        for ex_link in external_links:
            logger.info("link_name: {}, link: {}".format(ex_link["link_name"], ex_link["link"]))
        photo = json.loads(content["photo"])
        for p in photo:
            logger.info("gcs_url: {}".format(p["gcs_url"]))
        if limit_cnt > 0 and idx == limit_cnt - 1:
            break
        logger.info("------------------------------------------------------------")


if __name__ == '__main__':
    url = "https://icamping-prod.appspot.com/_ah/api/icamping_guest/v2/showallstores"
    process(url)
