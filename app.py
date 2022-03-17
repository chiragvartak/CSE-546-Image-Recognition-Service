from time import time, sleep
from math import inf
import logging
from fr import face_match
import boto3
import json
import base64
import os
import threading
import socket

# Constants
AWS_REGION = "us-east-1"
DATA_MODEL_PATH = "/home/ec2-user/data.pt"
CURRENT_IMAGE_SAVE_PATH = "/home/ec2-user/current.jpg"
REQUEST_QUEUE_NAME = "cc-project-req-sqs"
RESPONSE_QUEUE_NAME = "cc-project-res-sqs"
DELETE_SQS_MESSAGES_AFTER_RETRIEVING = True

# Globals
hostname = socket.gethostname()

# Logging. Source: example on https://docs.python.org/3/howto/logging.html
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Initializing resources
sqs = boto3.resource('sqs', region_name=AWS_REGION)
requestQueue = sqs.get_queue_by_name(QueueName=REQUEST_QUEUE_NAME)
responseQueue = sqs.get_queue_by_name(QueueName=RESPONSE_QUEUE_NAME)

# Testing code below - delete it!
# testImagePath = "/home/ec2-user/mine/face_images_100/test_00.jpg"
# image_test_00 = "data:image/jpeg;base64,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"


def delete_request_from_queue(handle):
    sqs_response = requestQueue.delete_messages(
        Entries=[{
            'Id': '0',
            'ReceiptHandle': handle
        }]
    )
    # print('Deleted message in app: %s' % sqs_response)


def waitTillAnItemAvailableInRequestQueue():
    "Waits till an item is available in the request queue, retrieves it and then deletes it. Returns the item as the tuple (userid:string, image:base64string)"
    logger.info("Waiting for an item to be available in the request queue ...")
    messages = None
    while messages is None or len(messages) == 0:
        messages = requestQueue.receive_messages(
            QueueUrl=requestQueue.url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20,  # If infinite was allowed I'd set it to that. But the max allowed is 20 secs.
            MessageAttributeNames=['All']
        )
    msgJson = json.loads(messages[0].body)
    message_file_name, message_id = msgJson['message_id'].split('___')

    logger.info("... retrieved message from the request queue. The request id is " + msgJson["message_id"])
    if DELETE_SQS_MESSAGES_AFTER_RETRIEVING:
        handle = messages[0].receipt_handle
        delete_request_from_queue(handle)
    logger.info("Deleted message %s from the request queue." % msgJson["message_id"])
    return message_id, message_file_name, msgJson["image"]





def saveImage(image):
    "Takes a Base64 image string, saves it to a path, and returns that path"
    logger.info("Decoding the image from Base64 and making a jpg image file ...")
    imgData = base64.b64decode(image)
    with open(CURRENT_IMAGE_SAVE_PATH, "wb") as fh:
        fh.write(imgData)
    logger.info("... decoded image.")
    return CURRENT_IMAGE_SAVE_PATH


def findOutput(image):
    imagePath = saveImage(image)
    logger.info("Identifying the image ...")
    personName, confidence = face_match(imagePath, DATA_MODEL_PATH)
    logger.info("... image identified. It's %s." % personName)
    return personName


def addToResponseQueue(message_id, personName, time_taken):
    messageBody = {
        "message_id": message_id,
        "response": personName,
        "time_taken": time_taken,
        "ec2_name": hostname
    }
    messageBodyStr = json.dumps(messageBody)
    logger.info("Sending response to queue: %s ..." % messageBodyStr)
    sqs_response = responseQueue.send_message(
        QueueUrl=responseQueue.url,
        MessageAttributes={},
        MessageBody=messageBodyStr
    )
    logger.info("... response sent to queue.")


# The current image is stored in the file "current.jpg" and the recognized person name is passed as a parameter
def storeToS3(requestID, file_name, personName):
    logger.info("Uploading to S3 bucket..")
    s3client = boto3.client('s3')
    s3client.upload_file(
    '/home/ec2-user/current.jpg', '546inputchirag', file_name + '.jpg',
    ExtraArgs={'Metadata': {'RequestID': requestID}})

    # Writing classification result to a text file for Storage
    with open('/home/ec2-user/personName.txt', 'w') as f:
        f.write(personName)
    
    s3client.upload_file(
    '/home/ec2-user/personName.txt', '546outputchirag', file_name + '.txt',
    ExtraArgs={'Metadata': {'RequestID': requestID}})

    logger.info("S3 Upload complete..")





if __name__ == "__main__":
    while True:
        requestId, file_name, image = waitTillAnItemAvailableInRequestQueue()
        startTime = time()
        personName = findOutput(image)
        endTime = time()
        timeTakenToRecognizeImage = "%.1fs" % (endTime-startTime)
        addToResponseQueue(requestId, personName, timeTakenToRecognizeImage)
        storeToS3(requestId, file_name, personName)
