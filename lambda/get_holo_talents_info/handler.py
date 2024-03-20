import os
import boto3

BUCKET_NAME = os.environ['BUCKET_NAME']
FILE_PATH = 'hololive/talents.json'

s3 = boto3.client('s3')


def main(event, context):
    # S3からJSONファイルを取得しBodyで返却する
    bucket = BUCKET_NAME
    key = FILE_PATH
    response = s3.get_object(Bucket=bucket, Key=key)
    body = response['Body'].read()
    return {
        'headers': {
            "Content-type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        'statusCode': 200,
        'body': body,
    }
