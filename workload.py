import requests
import json

if __name__ == "__main__":
    # url = 'http://127.0.0.1:5000/recognize'
    url = "http://ec2-3-95-191-11.compute-1.amazonaws.com:5000/recognize"
    # url = "http://3.95.191.11:5000/recognize"
    # image_path = '/Users/siddhantsrivastava/Desktop/test_03.jpeg'
    image_path = '/Users/chirag/Downloads/face_images_100/test_00.jpg'

    file = {"myfile": open(image_path, 'rb')}
    r = json.loads(requests.post(url, files=file).text)

    print(r)
