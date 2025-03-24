import boto3
import json
import uuid

dynamodb = boto3.resource('dynamodb')
ec2 = boto3.client('ec2')

# DynamoDB Table Name
DYNAMODB_TABLE = "VpcDetails"

def create_vpc_and_subnets(event, context):
    try:
        # Create VPC
        vpc_response = ec2.create_vpc(
            CidrBlock='10.0.0.0/16',
            AmazonProvidedIpv6CidrBlock=True,
            InstanceTenancy='default'
        )
        vpc_id = vpc_response['Vpc']['VpcId']

        # Create Subnets
        subnet1_response = ec2.create_subnet(
            CidrBlock='10.0.1.0/24',
            VpcId=vpc_id,
            AvailabilityZone='us-east-1a'
        )
        subnet2_response = ec2.create_subnet(
            CidrBlock='10.0.2.0/24',
            VpcId=vpc_id,
            AvailabilityZone='us-east-1b'
        )
        subnet1_id = subnet1_response['Subnet']['SubnetId']
        subnet2_id = subnet2_response['Subnet']['SubnetId']

        # Store the details in DynamoDB
        table = dynamodb.Table(DYNAMODB_TABLE)
        item = {
            'VpcId': vpc_id,
            'VpcName': f'Vpc-{str(uuid.uuid4())}',
            'Subnets': [subnet1_id, subnet2_id],
            'CreatedAt': str(context.timestamp)
        }

        table.put_item(Item=item)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'VPC and Subnets created successfully!',
                'vpc_id': vpc_id,
                'subnets': [subnet1_id, subnet2_id]
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def get_vpc_details(event, context):
    try:
        # Retrieve data from DynamoDB
        vpc_id = event['pathParameters']['vpc_id']
        table = dynamodb.Table(DYNAMODB_TABLE)
        response = table.get_item(
            Key={'VpcId': vpc_id}
        )

        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'VPC not found'})
            }

        vpc_details = response['Item']

        return {
            'statusCode': 200,
            'body': json.dumps(vpc_details)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
