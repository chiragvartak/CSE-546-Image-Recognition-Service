import subprocess
import os

# subprocess.run(["ffmpeg", "-i", "1.jpeg", "-filter:v", "crop=1200:1200:100:150", "1.png"])
# ffmpeg -i 3.png -filter:v "crop=1200:1200:100:150" 3cropped.png
def cropAndConvertToPng():
    for jpeg in os.listdir(""):
        base, ext = jpeg.split(".")
        if ext == "jpeg":
            subprocess.run(["ffmpeg", "-i", jpeg, "-filter:v", "crop=700:700:50:150", f"{base}.png"])

# Convert to 160x160
# ffmpeg -i 3.png -vf scale=160:160 output_160.png
def convertTo160x160():
    for png in os.listdir(""):
        base, ext = png.split(".")
        if ext == "png":
            subprocess.run(["ffmpeg", "-i", png, "-vf", "scale=160:160", f"{base}_160.png"])

if __name__ == "__main__":
    # cropAndConvertToPng()
    convertTo160x160()