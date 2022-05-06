from pathlib import Path
from PIL import Image

folder = "siddhant"
heightOffset = 0

def crop_image(img):
    width, height = img.size
    newWidth, newHeight = min(width,height), min(width,height)
    area = (0, heightOffset, newWidth, newHeight+heightOffset)
    return img.crop(area)

if __name__ == "__main__":
    folderPath = Path(folder)
    for file in folderPath.iterdir():
        if (not file.is_file()) or (file.suffix != '.jpeg'):
            continue
        img = Image.open(file)
        img = crop_image(img)  # Crop the image and make it a square
        img = img.resize(size=(160, 160))  # Reduce the dimensions of the image to 160x160
        saveFile = Path(file.stem + "_1" + file.suffix)
        img.save(saveFile)
