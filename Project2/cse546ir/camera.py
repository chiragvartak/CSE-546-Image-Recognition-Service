from time import sleep
from picamera import PiCamera
import logging
import boto3
from botocore.exceptions import ClientError
import os

s3_client = boto3.client('s3')
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 40
count = 1

while True:
    print('Recording a new 10 second clip in 3')
    sleep(1)
    print('2')
    sleep(1)
    print('1')
    sleep(1)

    # Starting recording
    camera.start_recording('video_' + str(count) +'.h264')
    print('Recording...')
    camera.wait_recording(10)
    camera.stop_recording()
    print('Done recording, saved to Desktop/video_' + str(count) + '.h264')

    # S3 Upload
    print('Uploading to S3..')
    s3_client.upload_file(Filename='/home/pi/Desktop/video_' + str(count) + '.h264', Bucket="546videos", Key='video' + str(count) + '.h264')

    count += 1
    
