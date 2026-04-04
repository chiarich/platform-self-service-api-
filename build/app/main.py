import boto3
import uuid

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
    print(f"create_s3_bucket called with bucket_name={bucket_name}, region={region}")

    if region == "us-east-1":
        s3.create_bucket(Bucket=bucket_name)
    else:
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": region},
        )

    print(f"S3 bucket creation request completed for {bucket_name}")


@app.get("/")
def root():
    return {"message": "Platform Self Service API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/buckets", response_model=BucketResponse)
def create_bucket(bucket: BucketRequest):
    request_id = str(uuid.uuid4())
    print(f"create_bucket called for bucket_name={bucket.bucket_name}, request_id={request_id}")

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
        print("Checking whether bucket already exists")

        try:
            s3.head_bucket(Bucket=bucket.bucket_name)
            print(f"Bucket already exists globally: {bucket.bucket_name}")
            raise HTTPException(
                status_code=400,
                detail="Bucket already exists globally",
            )
        except ClientError as head_exc:
            error_code = head_exc.response.get("Error", {}).get("Code", "Unknown")
            print(f"head_bucket response code for {bucket.bucket_name}: {error_code}")

        print("Creating S3 bucket now")
        create_s3_bucket(bucket.bucket_name, "us-east-1")

        print("Saving request metadata to DynamoDB")
        table.put_item(Item=item)
        print(f"DynamoDB item saved for request_id={request_id}")

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
        error_message = exc.response["Error"]["Message"]
        print(f"AWS ClientError during create_bucket: {error_message}")
        raise HTTPException(
            status_code=500,
            detail=f"AWS error: {error_message}",
        ) from exc
    except Exception as exc:
        print(f"Unexpected error during create_bucket: {str(exc)}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(exc)}",
        ) from exc


@app.get("/buckets")
def get_buckets():
    print("get_buckets called")
    try:
        response = table.scan()
        items = response.get("Items", [])
        print(f"get_buckets returning {len(items)} items")
        return items
    except ClientError as exc:
        error_message = exc.response["Error"]["Message"]
        print(f"AWS ClientError during get_buckets: {error_message}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch bucket requests: {error_message}",
        ) from exc


@app.get("/buckets/{bucket_id}")
def get_bucket(bucket_id: str):
    print(f"get_bucket called for bucket_id={bucket_id}")
    try:
        response = table.get_item(Key={"id": bucket_id})
        item = response.get("Item")

        if not item:
            print(f"Bucket not found for id={bucket_id}")
            raise HTTPException(status_code=404, detail="Bucket not found")

        print(f"Bucket found for id={bucket_id}")
        return item
    except ClientError as exc:
        error_message = exc.response["Error"]["Message"]
        print(f"AWS ClientError during get_bucket: {error_message}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch bucket request: {error_message}",
        ) from exc


@app.put("/buckets/{bucket_id}")
def update_bucket(bucket_id: str, bucket: BucketRequest):
    print(f"update_bucket called for bucket_id={bucket_id}")
    try:
        response = table.get_item(Key={"id": bucket_id})
        if "Item" not in response:
            print(f"Bucket not found for update: {bucket_id}")
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

        print(f"Bucket updated successfully for id={bucket_id}")
        return {
            "message": "Bucket updated successfully",
            "id": bucket_id,
        }
    except ClientError as exc:
        error_message = exc.response["Error"]["Message"]
        print(f"AWS ClientError during update_bucket: {error_message}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update bucket request: {error_message}",
        ) from exc


@app.delete("/buckets/{bucket_id}")
def delete_bucket(bucket_id: str):
    print(f"delete_bucket called for bucket_id={bucket_id}")
    try:
        response = table.get_item(Key={"id": bucket_id})
        if "Item" not in response:
            print(f"Bucket not found for delete: {bucket_id}")
            raise HTTPException(status_code=404, detail="Bucket not found")

        table.delete_item(Key={"id": bucket_id})
        print(f"Bucket deleted successfully for id={bucket_id}")

        return {"message": "Bucket deleted successfully", "id": bucket_id}
    except ClientError as exc:
        error_message = exc.response["Error"]["Message"]
        print(f"AWS ClientError during delete_bucket: {error_message}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete bucket request: {error_message}",
        ) from exc


handler = Mangum(app)