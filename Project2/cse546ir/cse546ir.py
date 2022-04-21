import json
import urllib.parse
import boto3
import os

print('Loading function')

s3 = boto3.client('s3')


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    print("INPUT BUCKET AND KEY:  { Bucket: '%s', Key: '%s' }" % (bucket, key))

    save_file = '/tmp/%s' % key
    frame_save_regex = 'frame_%s_%s.jpeg' % (key.split('.')[0].split('_')[1], '%02d')
    s3.download_file(bucket, key, save_file)

    try:
        os.system('ffmpeg -i %s -r 2 %s' % (save_file, frame_save_regex))
        os.remove(save_file)
        
        for frame_filename in os.listdir('/tmp'):
            if frame_filename.endswith('.jpeg') and frame_filename.split('.')[0].split('_')[1] == key.split('.')[0].split('_')[1]:
                response = s3.upload_file(os.path.join('/tmp', frame_filename), 'cc-project2-frame-bucket', frame_filename)
                print('FRAME %s UPLOADED\nRESPONSE: %s' % (frame_filename, response))
                os.remove(os.path.join('/tmp', frame_filename))
    except Exception as e:
        print(e)
        return False
    return True
