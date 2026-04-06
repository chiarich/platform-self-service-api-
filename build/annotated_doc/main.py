import logging
import os
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError
from fastapi import FastAPI, HTTPException
from mangum import Mangum
from pydantic import BaseModel, Field, field_validator

# --------------------------------------------------
# Logging
# --------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# AWS clients/resources
# --------------------------------------------------
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
TABLE_NAME = os.getenv("TABLE_NAME", "platform-api-dev-buckets")

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(TABLE_NAME)
s3 = boto3.client("s3", region_name=AWS_REGION)

# --------------------------------------------------
# FastAPI app
# --------------------------------------------------
app = FastAPI(
    title="Platform Self-Service API",
    version="1.0.0",
    description="Self-service API for provisioning S3 buckets and tracking requests in DynamoDB.",
)


# --------------------------------------------------
# Helpers
# --------------------------------------------------
def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def decimal_to_native(value: Any) -> Any:
    if isinstance(value, list):
        return [decimal_to_native(v) for v in value]
    if isinstance(value, dict):
        return {k: decimal_to_native(v) for k, v in value.items()}
    if isinstance(value, Decimal):
        if value % 1 == 0:
            return int(value)
        return float(value)
    return value


def get_existing_bucket_by_name(bucket_name: str) -> Optional[Dict[str, Any]]:
    response = table.scan(
        FilterExpression="bucket_name = :bucket_name",
        ExpressionAttributeValues={":bucket_name": bucket_name},
    )
    items = response.get("Items", [])
    return items[0] if items else None


def validate_s3_bucket_name(bucket_name: str) -> str:
    name = bucket_name.strip()

    if not name:
        raise HTTPException(status_code=422, detail="bucket_name is required")

    if len(name) < 3 or len(name) > 63:
        raise HTTPException(
            status_code=422,
            detail="bucket_name must be between 3 and 63 characters",
        )

    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789.-")
    if any(ch not in allowed for ch in name):
        raise HTTPException(
            status_code=422,
            detail="bucket_name must contain only lowercase letters, numbers, dots, and hyphens",
        )

    if ".." in name or ".-" in name or "-." in name:
        raise HTTPException(
            status_code=422,
            detail="bucket_name contains an invalid dot/hyphen sequence",
        )

    if name.startswith(".") or name.endswith(".") or name.startswith("-") or name.endswith("-"):
        raise HTTPException(
            status_code=422,
            detail="bucket_name cannot start or end with a dot or hyphen",
        )

    return name


# --------------------------------------------------
# Models
# --------------------------------------------------
class BucketCreateRequest(BaseModel):
    team_name: str = Field(..., min_length=2, max_length=50)
    environment: str = Field(..., min_length=2, max_length=20)
    bucket_name: str = Field(..., min_length=3, max_length=63)
    purpose: str = Field(..., min_length=3, max_length=200)

    @field_validator("team_name", "environment", "purpose")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("bucket_name")
    @classmethod
    def normalize_bucket_name(cls, value: str) -> str:
        return validate_s3_bucket_name(value.lower())


class BucketUpdateRequest(BaseModel):
    purpose: Optional[str] = Field(default=None, min_length=3, max_length=200)
    environment: Optional[str] = Field(default=None, min_length=2, max_length=20)

    @field_validator("purpose", "environment")
    @classmethod
    def strip_optional_text(cls, value: Optional[str]) -> Optional[str]:
        return value.strip() if value else value


class BucketResponse(BaseModel):
    id: str
    status: str
    message: str
    bucket_name: str
    team_name: str
    environment: str
    purpose: Optional[str] = None
    created_at: Optional[str] = None


# --------------------------------------------------
# Routes
# --------------------------------------------------
@app.get("/")
def root() -> Dict[str, str]:
    return {
        "message": "Platform Self-Service API is running",
        "docs": "/docs",
    }


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "healthy"}


@app.get("/buckets")
def get_buckets() -> Dict[str, List[Dict[str, Any]]]:
    try:
        response = table.scan()
        items = decimal_to_native(response.get("Items", []))
        return {"items": items}
    except ClientError as exc:
        logger.exception("Failed to list buckets")
        raise HTTPException(status_code=500, detail="Failed to list bucket records") from exc


@app.get("/buckets/{bucket_id}")
def get_bucket(bucket_id: str) -> Dict[str, Any]:
    try:
        response = table.get_item(Key={"id": bucket_id})
        item = response.get("Item")

        if not item:
            raise HTTPException(status_code=404, detail="Bucket not found")

        return decimal_to_native(item)
    except HTTPException:
        raise
    except ClientError as exc:
        logger.exception("Failed to get bucket with id %s", bucket_id)
        raise HTTPException(status_code=500, detail="Failed to get bucket") from exc


@app.post("/buckets", response_model=BucketResponse)
def create_bucket(payload: BucketCreateRequest) -> BucketResponse:
    logger.info(
        "Received bucket create request",
        extra={
            "team_name": payload.team_name,
            "environment": payload.environment,
            "bucket_name": payload.bucket_name,
        },
    )

    try:
        existing = get_existing_bucket_by_name(payload.bucket_name)
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Bucket '{payload.bucket_name}' already exists",
            )

        # Check in AWS as well
        try:
            s3.head_bucket(Bucket=payload.bucket_name)
            raise HTTPException(
                status_code=409,
                detail=f"Bucket '{payload.bucket_name}' already exists",
            )
        except ClientError as head_exc:
            error_code = head_exc.response.get("Error", {}).get("Code", "")
            if error_code not in {"404", "NoSuchBucket", "NotFound"}:
                # 403 may also mean the bucket exists but is owned by another account
                if error_code == "403":
                    raise HTTPException(
                        status_code=409,
                        detail=f"Bucket '{payload.bucket_name}' already exists or is not accessible",
                    )
                raise

        if AWS_REGION == "us-east-1":
            s3.create_bucket(Bucket=payload.bucket_name)
        else:
            s3.create_bucket(
                Bucket=payload.bucket_name,
                CreateBucketConfiguration={"LocationConstraint": AWS_REGION},
            )

        s3.put_bucket_tagging(
            Bucket=payload.bucket_name,
            Tagging={
                "TagSet": [
                    {"Key": "Project", "Value": "platform-self-service-api"},
                    {"Key": "Team", "Value": payload.team_name},
                    {"Key": "Environment", "Value": payload.environment},
                    {"Key": "Purpose", "Value": payload.purpose},
                ]
            },
        )

        request_id = str(uuid.uuid4())
        item = {
            "id": request_id,
            "team_name": payload.team_name,
            "environment": payload.environment,
            "bucket_name": payload.bucket_name,
            "purpose": payload.purpose,
            "status": "created",
            "created_at": now_utc_iso(),
        }

        table.put_item(Item=item)

        return BucketResponse(
            id=request_id,
            status="success",
            message="Bucket created successfully",
            bucket_name=payload.bucket_name,
            team_name=payload.team_name,
            environment=payload.environment,
            purpose=payload.purpose,
            created_at=item["created_at"],
        )

    except HTTPException:
        raise
    except ClientError as exc:
        logger.exception("AWS error while creating bucket")
        raise HTTPException(status_code=500, detail="AWS error while creating bucket") from exc
    except Exception as exc:
        logger.exception("Unexpected error while creating bucket")
        raise HTTPException(status_code=500, detail="Unexpected error while creating bucket") from exc


@app.put("/buckets/{bucket_id}")
def update_bucket(bucket_id: str, payload: BucketUpdateRequest) -> Dict[str, Any]:
    try:
        response = table.get_item(Key={"id": bucket_id})
        item = response.get("Item")

        if not item:
            raise HTTPException(status_code=404, detail="Bucket not found")

        updated_item = dict(item)

        if payload.environment is not None:
            updated_item["environment"] = payload.environment

        if payload.purpose is not None:
            updated_item["purpose"] = payload.purpose

        updated_item["updated_at"] = now_utc_iso()

        table.put_item(Item=updated_item)
        return {
            "message": "Bucket record updated successfully",
            "item": decimal_to_native(updated_item),
        }

    except HTTPException:
        raise
    except ClientError as exc:
        logger.exception("Failed to update bucket record %s", bucket_id)
        raise HTTPException(status_code=500, detail="Failed to update bucket record") from exc


@app.delete("/buckets/{bucket_id}")
def delete_bucket(bucket_id: str) -> Dict[str, str]:
    try:
        response = table.get_item(Key={"id": bucket_id})
        item = response.get("Item")

        if not item:
            raise HTTPException(status_code=404, detail="Bucket not found")

        bucket_name = item["bucket_name"]

        try:
            s3.delete_bucket(Bucket=bucket_name)
        except ClientError as exc:
            error_code = exc.response.get("Error", {}).get("Code", "")
            if error_code in {"NoSuchBucket", "404", "NotFound"}:
                logger.warning("S3 bucket %s already missing; removing record anyway", bucket_name)
            else:
                logger.exception("Failed to delete S3 bucket %s", bucket_name)
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to delete S3 bucket '{bucket_name}'",
                ) from exc

        table.delete_item(Key={"id": bucket_id})

        return {
            "message": f"Bucket '{bucket_name}' deleted successfully",
            "id": bucket_id,
        }

    except HTTPException:
        raise
    except ClientError as exc:
        logger.exception("Failed to delete bucket record %s", bucket_id)
        raise HTTPException(status_code=500, detail="Failed to delete bucket") from exc


# --------------------------------------------------
# Lambda handler
# --------------------------------------------------
handler = Mangum(app)