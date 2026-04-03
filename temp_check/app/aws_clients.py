import os

import boto3


AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


def get_s3_client():
    return boto3.client("s3", region_name=AWS_REGION)


def get_dynamodb_resource():
    return boto3.resource("dynamodb", region_name=AWS_REGION)