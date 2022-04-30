# Set environment variables even before importing the module - you never know which modules use which env variables
import os
os.environ["TORCH_HOME"] = "/tmp/PyTorchHome"

import json
import urllib.parse
import boto3
import subprocess
import time
import eval_face_recognition2

print('Loading function')

session = boto3.Session(
    aws_access_key_id='',
    aws_secret_access_key='',
)

s3 = session.client('s3')
dynamodb = session.client('dynamodb', region_name='us-east-1')
sqs = session.client('sqs', region_name='us-east-1')
queue = sqs.get_queue_by_name(QueueName='cc-project2-response-queue')

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    print("INPUT BUCKET AND KEY:  { Bucket: '%s', Key: '%s' }" % (bucket, key))

    save_file = '/tmp/%s' % key
    frame_save_regex = '/tmp/frame_%s_%s.jpeg' % (key.split('.')[0].split('_')[1], '%02d')
    s3.download_file(bucket, key, save_file)
    
    start = time.time()
    # process_response = subprocess.run(['ffmpeg', '-sseof', '5', '-i', save_file, '-vframes', '1', '/tmp/end.jpeg'], capture_output=True)
    process_response = subprocess.run(['ffmpeg', '-i', save_file, '-vf', 'fps=1/0.5', '/tmp/img%03d.jpeg'], capture_output=True)
    print('TIME: %s' % str(time.time()-start))

    # ls_process = subprocess.Popen(["ls", "-l", '/tmp'], stdout=subprocess.PIPE)
    # out, err = ls_process.communicate()
    # print(out)

    for frame_filename in os.listdir('/tmp'):
        if frame_filename.endswith('.jpeg'):
            print(frame_filename)
            result = eval_face_recognition2.evalImage("/tmp/" + frame_filename)
            print('INFO: FACE RECOGNIZED AS: %s' % result)

            db_item = dynamodb.get_item(
                TableName='cc-project2-info-table',
                Key={
                    'name': {'S': 'siddhant'}
                }
            )['Item']
            print('INFO: ITEM FETCHED FROM DYNAMO DB: %s' % db_item)

            sqs_response = queue.send_message(
                QueueUrl=queue.url,
                MessageAttributes={},
                MessageBody=json.dumps(response['Item'])
            )
            print('INFO: SQS RESPONSE: %s' % (sqs_response))
    return True
