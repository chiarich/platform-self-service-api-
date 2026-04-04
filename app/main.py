import uuid
import boto3

from fastapi import FastAPI, HTTPException
from mangum import Mangum
from botocore.exceptions import ClientError

from app.models import BucketRequest, BucketResponse
from app.db import table

s3 = boto3.client("s3", region_name="us-east-1")

app = FastAPI(
    title="Platform Self-Service API",
    version="0.1.0",
    description="Internal API for standardized bucket provisioning requests",
)


def create_s3_bucket(bucket_name: str, region: str = "us-east-1") -> None:
    if region == "us-east-1":
        s3.create_bucket(Bucket=bucket_name)
    else:
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": region},
        )


@app.get("/")
def root():
    return {"message": "Platform Self Service API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/buckets", response_model=BucketResponse)
def create_bucket(bucket: BucketRequest):
    request_id = str(uuid.uuid4())

    item = {
        "id": request_id,
        "request_id": request_id,
        "team_name": bucket.team_name,
        "environment": bucket.environment,
        "bucket_name": bucket.bucket_name,
        "purpose": bucket.purpose,
        "status": "created",
        "message": "Bucket request created successfully",
    }

    try:
        # Check if bucket already exists in S3
        try:
            s3.head_bucket(Bucket=bucket.bucket_name)
            raise HTTPException(
                status_code=409,
                detail=f"Bucket '{bucket.bucket_name}' already exists",
            )
        except ClientError as e:
            error_code = str(e.response.get("Error", {}).get("Code", ""))

            # These mean "not found" / safe to continue
            if error_code not in ["404", "NoSuchBucket", "NotFound"]:
                raise HTTPException(
                    status_code=409,
                    detail=f"Bucket '{bucket.bucket_name}' already exists or is not available",
                )

        # Create the bucket
        create_s3_bucket(bucket.bucket_name)

        # Save request metadata to DynamoDB
        table.put_item(Item=item)

        return BucketResponse(
            request_id=request_id,
            status="created",
            message="Bucket created successfully",
            bucket_name=bucket.bucket_name,
            team_name=bucket.team_name,
            environment=bucket.environment,
        )

    except HTTPException:
        raise
    except ClientError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"AWS error: {exc.response['Error']['Message']}",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(exc)}",
        ) from exc


@app.get("/buckets")
def get_buckets():
    try:
        response = table.scan()
        return response.get("Items", [])
    except ClientError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch bucket requests: {exc.response['Error']['Message']}",
        ) from exc


@app.get("/buckets/{bucket_id}")
def get_bucket(bucket_id: str):
    try:
        response = table.get_item(Key={"id": bucket_id})
        item = response.get("Item")

        if not item:
            raise HTTPException(status_code=404, detail="Bucket not found")

        return item
    except ClientError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch bucket request: {exc.response['Error']['Message']}",
        ) from exc


@app.put("/buckets/{bucket_id}")
def update_bucket(bucket_id: str, bucket: BucketRequest):
    try:
        response = table.get_item(Key={"id": bucket_id})
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Bucket not found")

        table.update_item(
            Key={"id": bucket_id},
            UpdateExpression="""
                SET team_name = :team_name,
                    environment = :environment,
                    bucket_name = :bucket_name,
                    purpose = :purpose,
                    #status = :status,
                    message = :message
            """,
            ExpressionAttributeNames={
                "#status": "status",
            },
            ExpressionAttributeValues={
                ":team_name": bucket.team_name,
                ":environment": bucket.environment,
                ":bucket_name": bucket.bucket_name,
                ":purpose": bucket.purpose,
                ":status": "updated",
                ":message": "Bucket request updated successfully",
            },
            ReturnValues="ALL_NEW",
        )

        return {
            "message": "Bucket updated successfully",
            "id": bucket_id,
        }
    except ClientError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update bucket request: {exc.response['Error']['Message']}",
        ) from exc


@app.delete("/buckets/{bucket_id}")
def delete_bucket(bucket_id: str):
    try:
        response = table.get_item(Key={"id": bucket_id})
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Bucket not found")

        table.delete_item(Key={"id": bucket_id})

        return {"message": "Bucket deleted successfully", "id": bucket_id}
    except ClientError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete bucket request: {exc.response['Error']['Message']}",
        ) from exc


handler = Mangum(app)