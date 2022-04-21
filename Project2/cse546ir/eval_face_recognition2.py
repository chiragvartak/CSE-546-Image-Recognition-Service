import torch
import torchvision.transforms as transforms
from PIL import Image
import json
import numpy as np
import build_custom_model
from time import time

labels_dir = "checkpoint/labels.json"
model_path = "checkpoint/model_vggface2_best.pth"

# read labels
with open(labels_dir) as f:
     labels = json.load(f)
# print(f"labels: {labels}")

device = torch.device('cpu')
model = build_custom_model.build_model(len(labels)).to(device)
model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu'))['model'])
model.eval()
# print(f"Best accuracy of the loaded model: {torch.load(model_path, map_location=torch.device('cpu'))['best_acc']}")

def evalImage(img_path: str) -> str:

     # parser = argparse.ArgumentParser(description='Evaluate your customized face recognition model')
     # parser.add_argument('--img_path', type=str, default="./data/test_me/val/angelina_jolie/1.png", help='the path of the dataset')
     # args = parser.parse_args()
     # img_path = args.img_path

     img = Image.open(img_path)
     img_tensor = transforms.ToTensor()(img).unsqueeze_(0).to(device)
     outputs = model(img_tensor)
     _, predicted = torch.max(outputs.data, 1)
     result = labels[np.array(predicted.cpu())[0]]
     # print(predicted.data, result)

     # img_name = img_path.split("/")[-1]
     # img_and_result = f"({img_name}, {result})"
     # print(f"Image and its recognition result is: {img_and_result}")

     return result

if __name__ == "__main__":
     start = time()
     result = evalImage("data/real_images/val/chirag/9_160.png")
     end = time()
     timeTaken = "%.2f" % (end - start)
     print("Result = %s, time taken = %ss" % (result, timeTaken))
