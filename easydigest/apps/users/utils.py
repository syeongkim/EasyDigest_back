import datetime
import random
import string
import boto3
from easydigest.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, AWS_S3_REGION_NAME

def s3_file_upload_by_file_data(upload_file, content_type=None):
    if content_type:
        content_type = content_type
    else:
        content_type = upload_file.content_type

    now = datetime.datetime.now()
    upload_file_name = f"{now}{upload_file.name}"

    try:
        upload_file.seek(0)
    except Exception:
        pass

    s3 = boto3.resource('s3', 
                        region_name=AWS_S3_REGION_NAME,
                        aws_access_key_id=AWS_ACCESS_KEY_ID, 
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    
    if s3.Bucket(AWS_STORAGE_BUCKET_NAME).put_object(
        Key=upload_file_name, 
        Body=upload_file, 
        ContentType=content_type, 
        ACL='public-read'
        ) is not None:
        return f"https://s3-{AWS_S3_REGION_NAME}.amazonaws.com/profile/{upload_file_name}"
    
    return False