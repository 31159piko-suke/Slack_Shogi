import boto3
from botocore.client import Config


def generate_presignedurl(user: str, ts: str):
    """
    Create a link to retrieve images from s3 with 12 hours validity.
    """
    S3_BUCKET_NAME = "slack-shogi"
    s3path = f"{user}/{ts}.jpg"

    s3 = boto3.client("s3", config=Config(signature_version="s3v4"))
    get_url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": S3_BUCKET_NAME,
            "Key": s3path,
        },
        ExpiresIn=43200,
        HttpMethod="GET",
    )
    return get_url


def put_s3_and_get_url(user: str, ts: str):
    """
    Upload an board image to s3 and return a link to retrieve the image.
    """
    S3_BUCKET_NAME = "slack-shogi"
    s3path = f"{user}/{ts}.jpg"

    s3 = boto3.resource("s3")
    obj = s3.Object(S3_BUCKET_NAME, s3path)
    img_bytes = open(f"/tmp/{user}:{ts}.jpg", "rb").read()
    obj.put(Body=img_bytes)

    geturl = generate_presignedurl(user, ts)

    return geturl
