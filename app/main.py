from fastapi import FastAPI, HTTPException
from mangum import Mangum
import uuid

from app.models import BucketRequest, BucketResponse
from app.db import table  # your DynamoDB table

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Platform Self Service API is running"}


# Create a new bucket
@app.post("/buckets", response_model=BucketResponse)
def create_bucket(bucket: BucketRequest):
    bucket_id = str(uuid.uuid4())  # auto-generate unique ID
    item = bucket.dict()
    item["id"] = bucket_id

    table.put_item(Item=item)

    return {
        "request_id": bucket_id,
        "status": "success",
        "message": "Bucket created",
        "bucket_name": bucket.bucket_name,
        "team_name": bucket.team_name,
        "environment": bucket.environment
    }


# Get all buckets
@app.get("/buckets")
def get_buckets():
    response = table.scan()
    return response.get("Items", [])


# Get a single bucket by id
@app.get("/buckets/{bucket_id}")
def get_bucket(bucket_id: str):
    response = table.get_item(Key={"id": bucket_id})

    if "Item" not in response:
        raise HTTPException(status_code=404, detail="Bucket not found")

    return response["Item"]


# Optional: Delete a bucket
@app.delete("/buckets/{bucket_id}")
def delete_bucket(bucket_id: str):
    table.delete_item(Key={"id": bucket_id})
    return {"message": "Bucket deleted"}


handler = Mangum(app)