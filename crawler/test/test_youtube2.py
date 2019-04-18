import os
import subprocess

import pytube

yt = pytube.YouTube("https://www.youtube.com/watch?v=iSkRGgYSQfY&list=PLOHZClinoCW7K_eX6MpKDUFc2Fmw0GvzJ")

vids = yt.streams.all()
for i in range(len(vids)):
    print(i, '. ', vids[i])

vnum = int(input("Enter vid num: "))

parent_dir = r"D:/temp/youtube/"
vids[vnum].download(parent_dir)

new_filename = input("Enter filename (including extension): ")
default_filename = vids[vnum].default_filename
subprocess.call(['ffmpeg', '-i', os.path.join(parent_dir, default_filename), os.path.join(parent_dir, new_filename)])

print("DONE ...")
