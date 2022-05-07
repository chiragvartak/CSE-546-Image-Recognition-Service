CSE-546 - Image Recognition Using Raspberry Pi

The steps to install and deploy the code are as follows:
1. Give access to AWS resources: Create an IAM role in AWS which has full access to the following AWS services: Lambda, ECR, S3, SQS, DynamoDB. Note down the access key id and secret. Put the access key if and secret obtained above in the "Project2/cse546ir/cse546ir.py" file.
2. Install the Python dependencies using the "requirements.txt" file provided.
3. Train the image recognition model: First set the proper member labels in the "checkpoint/labels.json" file. Put in properly preprocessed 160x160 pixel images in the "real_images/train" and "real_images/val" folders. Train the model using the following command:
$ python3 train_face_recognition.py --data_dir "data/real_images" --num_epochs 100
4. Build your docker image from the "Project2" folder. Upload your Docker image to the AWS ECR.
5. Create a Lambda function in AWS. Choose the Docker image you just uploaded as the run script for the Lambda. Increase Lambda memory so that it has a sufficient CPU. Set a trigger for the Lambda so that it is run on every create event on the configured S3 bucket.

On the Raspberry Pi:
1. After doing all the steps above, simply copy and paste the AWS access id and secret in the Raspberry Pi video upload script.
2. Configure the script to upload the videos to the correct S3 bucket.

If all the steps above have been configured correctly, simply start running the script on the Raspberry Pi. The script will upload videos to the S3, which in turn will trigger the Lambda. The recognized faces will be outputted to the SQS, which will then be retrieved from the Lambda and printed on the Raspberry Pi console.
