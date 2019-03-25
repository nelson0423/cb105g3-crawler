gmail = {"addr": "iiicb105g3@gmail.com", "pwd": "cb105g3-III"}
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
    print(days, "Days", hours, "Hours", minutes, "Minutes", seconds, "Seconds")


if __name__ == '__main__':
    print(gmail)
