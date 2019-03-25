import logging
import logging.config
import pandas as pd
import os
import json
import csv

log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_config.ini')
logging.config.fileConfig(log_file_path)
logger = logging.getLogger("crawler")

gmail = {"addr": "iiicb105g3@gmail.com", "pwd": "cb105g3-III"}
db_config = {
    "mongodb": "mongodb://localhost:27017/"
}
path_config = {
    "crawler": "/temp/crawler"
}


def stop_watch(value):
    valueD = (((value / 365) / 24) / 60)
    days = int(valueD)
    valueH = (valueD - days) * 365
    hours = int(valueH)
    valueM = (valueH - hours) * 24
    minutes = int(valueM)
    valueS = (valueM - minutes) * 60
    seconds = int(valueS)
    logging.info("Days: {}, Hours: {}, Minutes: {}, Seconds: {}".format(days, hours, minutes, seconds))


def json_to_csv(json_data, file_path):
    """
    JSON轉成CSV
    """
    pdir = os.path.dirname(file_path)
    if not os.path.exists(pdir):
        os.makedirs(pdir)
    pd.DataFrame(json_data).to_csv(file_path, header=True, index=False, quoting=csv.QUOTE_ALL, encoding="utf-8")


def csv_to_json(file_path):
    """
    CSV轉成JSON
    """
    df = pd.read_csv(file_path, encoding="utf-8")
    return json.loads(df.to_json(orient="records"))


# __all__ = ["logging"]

if __name__ == '__main__':
    print(os.path.abspath(__file__))
    print(os.path.dirname(os.path.abspath(__file__)))
    print(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_config.ini'))
