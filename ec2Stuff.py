import boto3

N = 2

ec2 = boto3.resource('ec2')

# create a new EC2 instance
for i in range(1, N+1):
    instances = ec2.create_instances(
        ImageId='ami-0a55e620aa5c79a24',
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName='ec2-nvi',
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'slave-'+str(i)
                    },
                ]
            }
        ],
    )
# instance.tags[0]["Value"]
# instance.private_dns_name


    print(instances)
# instances is [ec2.Instance(id='i-0f07f77a8fe59d816'), ec2.Instance(id='i-0ab56a528b0e0ffe7')]

### Terminate instances
# Source: https://intellipaat.com/community/42641/how-to-delete-an-ec2-instance-using-python-boto3#:~:text=all%20you%20need%20is%20to,value%20and%20you%20are%20done.

# import boto3
# ids = ['e1','e2','e3','e4','e5']
# ec2 = boto3.resource('ec2')
# ec2.instances.filter(InstanceIds = ids).terminate()
