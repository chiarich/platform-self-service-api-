import boto3
import os

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table(os.getenv("TABLE_NAME", "platform-api-dev-buckets"))