import boto3
import os

REGION = "us-east-1"
TABLE_NAME = "platform-api-dev-buckets"

dynamodb = boto3.resource("dynamodb", region_name=REGION)

table = dynamodb.Table(TABLE_NAME)