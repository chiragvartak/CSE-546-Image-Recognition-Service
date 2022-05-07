from time import sleep
from picamera import PiCamera
import logging
import boto3
from botocore.exceptions import ClientError
import os
import _thread as thread
import time
import json

# Access to S3 Bucket (Chirag)
ACCESS_KEY_ID = "AKIAYNOTAL3GXG7KINNF"
ACCESS_KEY_SECRET = "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"


AWS_REGION = "us-east-1"
RESPONSE_QUEUE_NAME = "cc-project2-response-queue"
session_chirag = boto3.Session(aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=ACCESS_KEY_SECRET)
s3_client = session_chirag.client('s3')

sqs = boto3.resource('sqs', region_name=AWS_REGION)
respQueue = sqs.get_queue_by_name(QueueName=RESPONSE_QUEUE_NAME)

camera = PiCamera()
camera.resolution = (640, 480)
count = 1


def delete_response_from_queue(handle):
    sqs_response = respQueue.delete_messages(
        Entries=[{
            'Id': '0',
            'ReceiptHandle': handle
        }]
    )

    #print('Deleted message in web: %s' % sqs_response, flush=True)

def sqsListen():
    person_count = 1
    while True:
        messages = None
        while messages is None or len(messages) == 0:
            #latency = time.time() - start_time
            messages = respQueue.receive_messages(
                QueueUrl=respQueue.url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=20,
                MessageAttributeNames=['All']
            )

        handle = messages[0].receipt_handle
        delete_response_from_queue(handle)

        # print Result + Latency
        resp_dict = json.loads(messages[0].body)
        print('The ' + str(person_count) + ' person recognized: "' + resp_dict['name']['S'] + '", "' + resp_dict['major']['S'] + '", "' + resp_dict['year']['S'] + '"')
        print('Latency: ' + str(resp_dict['time']))
        person_count += 1

thread.start_new_thread(sqsListen, ( ))
while True:
    # Starting recording
    camera.start_recording('/home/pi/Desktop/videos/video_' + str(count) +'.h264')
    print('Recording...')
    camera.wait_recording(2)
    camera.stop_recording()
    print('Done recording, saved to Desktop/videos/video_' + str(count) + '.h264')

    # S3 Upload
    print('Uploading to S3..')
    s3_client.upload_file(Filename='/home/pi/Desktop/videos/video_' + str(count) + '.h264', Bucket="cse546ir-s3-v2", Key='video' + str(count) + '.h264')
    #start_time = time.time()
    count += 1