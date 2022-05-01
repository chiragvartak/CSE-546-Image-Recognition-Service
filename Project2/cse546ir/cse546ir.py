import json
import urllib.parse
import boto3
import subprocess
import time
import os

startLoadingTime = time.time()
print('Loading function ...')
os.environ["TORCH_HOME"] = "/tmp/PyTorchHome"  # Set environment variables even before importing the modules - you
                                               # never know which modules use which env variables
import eval_face_recognition2

# Import private configs, if the private_config.py file exists
aws_access_key_id = ''
aws_secret_access_key = ''
try:
    import private_config
    aws_access_key_id = private_config.ACCESS_KEY_ID
    aws_secret_access_key = private_config.ACCESS_KEY_SECRET
except ModuleNotFoundError:
    pass

# Initialize AWS resources
session = boto3.Session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
s3 = session.client('s3')
dynamodb = session.client('dynamodb', region_name='us-east-1')
sqs = session.resource('sqs', region_name='us-east-1')
queue = sqs.get_queue_by_name(QueueName='cc-project2-response-queue')
print("... loaded function. Took %.3f secs" % (time.time()-startLoadingTime))


def lambda_handler(event, context):
    startLambdaTime = time.time()
    print("Received event: " + json.dumps(event))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    print("Input bucket and key: { Bucket: '%s', Key: '%s' }" % (bucket, key))

    save_file = '/tmp/%s' % key
    # frame_save_regex = '/tmp/frame_%s_%s.jpeg' % (key.split('.')[0].split('_')[1], '%02d')
    startVideoDownloadTime = time.time()
    s3.download_file(bucket, key, save_file)
    print("Time taken to download video: %.3f" % (time.time()-startVideoDownloadTime))
    
    startExtractFramesTime = time.time()
    # process_response = subprocess.run(['ffmpeg', '-sseof', '5', '-i', save_file, '-vframes', '1', '/tmp/end.jpeg'],
    #                                   capture_output=True)
    process_response = subprocess.run(['ffmpeg', '-i', save_file, '-vf', 'fps=1/0.5', '/tmp/img%03d.jpeg'],
                                      capture_output=True)
    print('Time taken to extract frames: %.3f' % (time.time()-startExtractFramesTime))

    for frame_filename in os.listdir('/tmp'):
        if frame_filename.endswith('.jpeg'):
            print(frame_filename)
            startImageRecognitionTime = time.time()
            result = eval_face_recognition2.evalImage("/tmp/" + frame_filename)
            print("Time taken for image recog: %.3f" % (time.time()-startImageRecognitionTime))
            print('Face recognized: %s' % result)

            db_item = dynamodb.get_item(
                TableName='cc-project2-info-table',
                Key={
                    'name': {'S': 'siddhant'}
                }
            )['Item']
            print('Item fetched from DynamoDb: %s' % db_item)

            sqs_response = queue.send_message(
                QueueUrl=queue.url,
                MessageAttributes={},
                MessageBody=json.dumps(response['Item'])
            )
            print('SQS Response: %s' % sqs_response)
    print("Time taken for lambda (excluding loading): %.3f" % (time.time()-startLambdaTime))
    return True
