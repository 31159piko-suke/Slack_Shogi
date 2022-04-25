import boto3
from botocore.client import Config
import requests


def generate_presignedurl(user: str, ts: str):
    bucket = "shogi-slack"
    s3path = f"{user}/{ts}.jpg"

    s3 = boto3.client("s3", config=Config(signature_version="s3v4"))
    put_url = s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": bucket,
            "Key": s3path,
        },
        ExpiresIn=3600,
        HttpMethod="PUT",
    )

    get_url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": bucket,
            "Key": s3path,
        },
        ExpiresIn=43200,
        HttpMethod="GET",
    )
    return put_url, get_url


def put_s3_and_get_url(user: str, ts: str):
    puturl, geturl = generate_presignedurl(user, ts)
    img_bytes = open(f"/tmp/{user}:{ts}.jpg", "rb").read()
    requests.put(url=puturl, data=img_bytes)
    return geturl
