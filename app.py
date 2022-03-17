from time import time
import logging
from fr import face_match
import boto3
import json
import base64
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


def delete_request_from_queue(handle):
    sqs_response = requestQueue.delete_messages(
        Entries=[{
            'Id': '0',
            'ReceiptHandle': handle
        }]
    )


def waitTillAnItemAvailableInRequestQueue():
    """Waits till an item is available in the request queue, retrieves it and then deletes it. Returns the item as
    the tuple (userid:string, file_name:string, image:base64string)"""
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
    """Takes a Base64 image string, saves it to a path, and returns that path"""
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
    logger.info("Uploading to S3 bucket ...")
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

    logger.info("... S3 Upload complete.")


if __name__ == "__main__":
    while True:
        requestId, file_name, image = waitTillAnItemAvailableInRequestQueue()
        startTime = time()
        personName = findOutput(image)
        endTime = time()
        timeTakenToRecognizeImage = "%.1fs" % (endTime - startTime)
        addToResponseQueue(requestId, personName, timeTakenToRecognizeImage)
        storeToS3(requestId, file_name, personName)
