import subprocess
import os

# subprocess.run(["ffmpeg", "-i", "1.jpeg", "-filter:v", "crop=1200:1200:100:150", "1.png"])
# ffmpeg -i 3.png -filter:v "crop=1200:1200:100:150" 3cropped.png
def cropAndConvertToPng():
    for jpeg in os.listdir("."):
        base, ext = jpeg.split(".")
        if ext == "jpg" and base.isnumeric() and 26<=int(base)<=35:
            subprocess.run(["ffmpeg", "-i", jpeg, "-filter:v", "crop=600:600:300:0", f"{base}.png"])

# Convert to 160x160
# ffmpeg -i 3.png -vf scale=160:160 output_160.png
def convertTo160x160():
    for png in os.listdir("."):
        base, ext = png.split(".")
        if ext == "png" and base.isnumeric() and 26<=int(base)<=35:
            subprocess.run(["ffmpeg", "-i", png, "-vf", "scale=160:160", f"{base}_160.png"])

if __name__ == "__main__":
    # cropAndConvertToPng()
    convertTo160x160()