from pytube import YouTube
import time
import ffmpy
import os

'''
Windows OS:
https://ffmpeg.zeranoe.com/builds/
下載並設定環境變數
'''

dir_path = "/youtube/"
mp4_dir_path = dir_path + "mp4/"
if not os.path.exists(mp4_dir_path):
    os.makedirs(mp4_dir_path)
mp3_dir_path = dir_path + "mp3/"
if not os.path.exists(mp3_dir_path):
    os.makedirs(mp3_dir_path)


def to_mp3(urls):
    for url in urls:
        try:
            yt = YouTube(url)
            print("=========================================================")
            print("Title:", yt.title)
            print("URL:", url)
            print("=========================================================")
            filename = yt.title
            filename = filename.replace(".", "．")
            filename = filename.replace("\\", "＼")
            filename = filename.replace("/", "／")
            print("Downloading ...")
            yt.streams.first().download(output_path=mp4_dir_path, filename=filename)
            time.sleep(1)
            mp4 = mp4_dir_path + filename + ".mp4"
            mp3 = mp3_dir_path + filename + ".mp3"
            ff = ffmpy.FFmpeg(inputs={mp4: None}, outputs={mp3: None})
            ff.run()
            print("Done ...")
        except Exception as e:
            print("[ERROR]", url, " >>>", e)


if __name__ == '__main__':
    urls = list()
    # urls.append("")
    urls.append("https://www.youtube.com/watch?v=fLexgOxsZu0")
    to_mp3(urls)
