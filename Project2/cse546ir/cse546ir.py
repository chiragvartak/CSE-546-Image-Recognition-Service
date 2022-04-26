import json
import urllib.parse
import boto3
import os
import subprocess
import time

print('Loading function')

session = boto3.Session(
    aws_access_key_id='',
    aws_secret_access_key='',
)
s3 = session.client('s3')


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
    process_response = subprocess.run(['ffmpeg', '-i', save_file, '-r', '2', frame_save_regex], capture_output=True)
    print('TIME: %s' % str(time.time()-start))

    for frame_filename in os.listdir('/tmp'):
        if frame_filename.endswith('.jpeg'):
            print('UPLOADING FRAME %s' % frame_filename)
            # response = s3.upload_file(os.path.join('/tmp', frame_filename), 'cc-project2-frame-bucket', frame_filename)
            print('FRAME %s UPLOADED' % frame_filename)

    return True
