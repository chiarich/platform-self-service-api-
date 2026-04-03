import uuid
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class ProvisioningError(Exception):
    pass


def create_bucket_request(payload):
    request_id = str(uuid.uuid4())
    final_bucket_name = f"{payload.team_name}-{payload.environment}-{payload.bucket_name}"

    logger.info(
        {
            "event": "bucket_request_received",
            "request_id": request_id,
            "team_name": payload.team_name,
            "environment": payload.environment,
            "bucket_name": final_bucket_name,
        }
    )

    return {
        "request_id": request_id,
        "status": "created",
        "message": "Bucket provisioned successfully (mock mode)",
        "bucket_name": final_bucket_name,
        "environment": payload.environment,
    }