import json
import boto3

client = boto3.client('dynamodb')

TABLE_NAME = "546proj2"

# Creating the DynamoDB Client
dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")

# Creating the DynamoDB Table Resource
dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
table = dynamodb.Table(TABLE_NAME)

response = table.get_item(
    Key={
        'name': 'nigel_wong'
    }
)
print(response['Item'])
