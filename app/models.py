from typing import Literal
import re

from pydantic import BaseModel, Field, field_validator

class BucketRequest(BaseModel):
    team_name: str = Field(..., min_length=2, max_length=30)
    environment: Literal["dev", "staging", "prod"]
    bucket_name: str = Field(..., min_length=3, max_length=63)
    purpose: str = Field(..., min_length=5, max_length=200)

    # Validators
    @field_validator("team_name")
    @classmethod
    def validate_team_name(cls, value: str) -> str:
        if not re.fullmatch(r"[a-z0-9-]+", value):
            raise ValueError(
                "team_name must contain only lowercase letters, numbers, and hyphens"
            )
        return value

    @field_validator("bucket_name")
    @classmethod
    def validate_bucket_name(cls, value: str) -> str:
        if not re.fullmatch(r"[a-z0-9.-]+", value):
            raise ValueError(
                "bucket_name must contain only lowercase letters, numbers, dots, and hyphens"
            )
        if ".." in value or ".-" in value or "-." in value:
            raise ValueError("bucket_name contains invalid adjacent characters")
        return value


class BucketResponse(BaseModel):
    request_id: str
    status: str
    message: str
    bucket_name: str
    team_name: str
    environment: str
