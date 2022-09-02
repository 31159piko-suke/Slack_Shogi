import os
import time
import boto3


def update_user(user_id):
    DYNAMODB_TABLE_NAME = "Slack_Shogi_UserManage"
    REGION_NAME = os.environ["AWS_REGION"]

    dynamodb = boto3.resource(service_name="dynamodb", region_name=REGION_NAME)
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    table.update_item(
        Key={"UserID": user_id},
        UpdateExpression="set LastCallTime=:lct add GamesPlayedNnumber :gpn",
        ExpressionAttributeValues={":lct": str(time.time()), ":gpn": 1},
    )
