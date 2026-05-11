import uuid

from fastapi import FastAPI, HTTPException, Query
from mangum import Mangum
from botocore.exceptions import ClientError

from app.models import BucketRequest, BucketResponse
from app.db import table
from app.aws_clients import get_s3_client

s3 = get_s3_client()

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


def empty_s3_bucket(bucket_name: str) -> None:
    paginator = s3.get_paginator("list_object_versions")
    objects_to_delete = []

    for page in paginator.paginate(Bucket=bucket_name):
        versions = page.get("Versions", [])
        for obj in versions:
            objects_to_delete.append({"Key": obj["Key"], "VersionId": obj["VersionId"]})
            if len(objects_to_delete) == 1000:
                s3.delete_objects(
                    Bucket=bucket_name,
                    Delete={"Objects": objects_to_delete, "Quiet": True},
                )
                objects_to_delete = []
                
        delete_markers = page.get("DeleteMarkers", [])
        for obj in delete_markers:
            objects_to_delete.append({"Key": obj["Key"], "VersionId": obj["VersionId"]})
            if len(objects_to_delete) == 1000:
                s3.delete_objects(
                    Bucket=bucket_name,
                    Delete={"Objects": objects_to_delete, "Quiet": True},
                )
                objects_to_delete = []

    if objects_to_delete:
        s3.delete_objects(
            Bucket=bucket_name,
            Delete={"Objects": objects_to_delete, "Quiet": True},
        )


def delete_s3_bucket(bucket_name: str) -> None:
    try:
        empty_s3_bucket(bucket_name)
        s3.delete_bucket(Bucket=bucket_name)
    except ClientError as exc:
        error_code = str(exc.response.get("Error", {}).get("Code", ""))
        if error_code in ["404", "NoSuchBucket", "NotFound"]:
            return
        raise


@app.get("/")
def root():
    return {"message": "Platform Self Service API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/buckets", response_model=BucketResponse)
def create_bucket(bucket: BucketRequest):
    request_id = str(uuid.uuid4())
    final_name = bucket.final_bucket_name

    item = {
        "id": request_id,
        "request_id": request_id,
        "team_name": bucket.team_name,
        "environment": bucket.environment,
        "bucket_name": final_name,
        "purpose": bucket.purpose,
        "status": "created",
        "message": "Bucket request created successfully",
    }

    try:
        try:
            s3.head_bucket(Bucket=final_name)
            raise HTTPException(
                status_code=409,
                detail=f"Bucket '{final_name}' already exists",
            )
        except ClientError as e:
            error_code = str(e.response.get("Error", {}).get("Code", ""))

            if error_code not in ["404", "NoSuchBucket", "NotFound"]:
                raise HTTPException(
                    status_code=409,
                    detail=f"Bucket '{final_name}' already exists or is not available",
                )

        create_s3_bucket(final_name)
        
        try:
            table.put_item(Item=item)
        except ClientError as db_exc:
            try:
                delete_s3_bucket(final_name)
            except Exception:
                pass
            raise db_exc

        return BucketResponse(
            request_id=request_id,
            status="created",
            message="Bucket created successfully",
            bucket_name=final_name,
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
def get_buckets(cursor: str = Query(None, description="Pagination cursor")):
    try:
        scan_kwargs = {}
        if cursor:
            scan_kwargs["ExclusiveStartKey"] = {"id": cursor}
            
        response = table.scan(**scan_kwargs)
        items = response.get("Items", [])
        last_evaluated_key = response.get("LastEvaluatedKey")
        
        return {
            "items": items,
            "next_cursor": last_evaluated_key.get("id") if last_evaluated_key else None
        }
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
    except HTTPException:
        raise
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

        existing_item = response["Item"]
        if bucket.final_bucket_name != existing_item.get("bucket_name"):
            raise HTTPException(
                status_code=400,
                detail="Cannot change bucket_name after creation"
            )

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
                ":bucket_name": bucket.final_bucket_name,
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
    except HTTPException:
        raise
    except ClientError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update bucket request: {exc.response['Error']['Message']}",
        ) from exc


@app.delete("/buckets/{bucket_id}")
def delete_bucket(bucket_id: str):
    try:
        response = table.get_item(Key={"id": bucket_id})
        item = response.get("Item")

        if not item:
            raise HTTPException(status_code=404, detail="Bucket not found")

        bucket_name = item["bucket_name"]

        delete_s3_bucket(bucket_name)
        table.delete_item(Key={"id": bucket_id})

        return {
            "message": "Bucket and record deleted successfully",
            "id": bucket_id,
            "bucket_name": bucket_name,
        }
    except HTTPException:
        raise
    except ClientError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete bucket and record: {exc.response['Error']['Message']}",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error while deleting bucket and record: {str(exc)}",
        ) from exc


handler = Mangum(app)