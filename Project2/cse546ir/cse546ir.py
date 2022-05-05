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
print("... loaded eval_face_recognition2. Took %.3f secs" % (time.time()-startLoadingTime))

# Import private configs, if the private_config.py file exists
aws_access_key_id, aws_secret_access_key = None, None
try:
    import private_config
    aws_access_key_id = private_config.ACCESS_KEY_ID
    aws_secret_access_key = private_config.ACCESS_KEY_SECRET
except ModuleNotFoundError:
    pass
aws_access_key_id_common, aws_secret_access_key_common = aws_access_key_id, aws_secret_access_key
try:
    aws_access_key_id_common = private_config.ACCESS_KEY_ID_COMMON
    aws_secret_access_key_common = private_config.ACCESS_KEY_SECRET_COMMON
except:
    pass

# Initialize AWS resources
session = boto3.Session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
s3 = session.client('s3')
session_common = boto3.Session(aws_access_key_id=aws_access_key_id_common,
                               aws_secret_access_key=aws_secret_access_key_common)
dynamodb = session_common.client('dynamodb', region_name='us-east-1')
sqs = session_common.resource('sqs', region_name='us-east-1')
queue = sqs.get_queue_by_name(QueueName='cc-project2-response-queue')
print("... loaded function. Took %s secs" % str(time.time()-startLoadingTime))


def lambda_handler(event, context):
    startLambdaTime = time.time()
    print("Received event: %s" % event)

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    print("Input bucket and key: { Bucket: '%s', Key: '%s' }" % (bucket, key))

    save_file = '/tmp/%s' % key
    startVideoDownloadTime = time.time()
    s3.download_file(bucket, key, save_file)
    print("Time taken to download video: %s" % str(time.time()-startVideoDownloadTime))
    
    startExtractFramesTime = time.time()
    process_response = subprocess.run(['ffmpeg', '-i', save_file, '-vf', 'fps=1/0.5', '/tmp/img%03d.jpeg'],
                                      capture_output=True)
    print('Time taken to extract frames: %s' % str(time.time()-startExtractFramesTime))

    for frame_filename in os.listdir('/tmp'):
        if frame_filename.endswith('.jpeg'):
            print(frame_filename)
            startImageRecognitionTime = time.time()
            result = eval_face_recognition2.evalImage("/tmp/" + frame_filename)
            print("Time taken for image recog: %s" % str(time.time()-startImageRecognitionTime))
            print('Face recognized: %s' % result)

            db_item = dynamodb.get_item(
                TableName='cc-project2-info-table',
                Key={
                    'name': {'S': result}
                }
            )['Item']
            db_item.update({
                'time': time.time() - startLambdaTime
            })
            print('Item fetched from DynamoDb: %s' % db_item)

            sqs_response = queue.send_message(
                QueueUrl=queue.url,
                MessageAttributes={},
                MessageBody=json.dumps(db_item)
            )
            print('SQS Response: %s' % sqs_response)
    print("Time taken for lambda (excluding loading): %s" % str(time.time()-startLambdaTime))
    return True
