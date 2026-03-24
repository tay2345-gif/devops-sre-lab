import os

os.environ["AWS_REGION"] = "us-east-1"
os.environ["S3_BUCKET"] = "my-test-bucket"
os.environ["SQS_URL"] = "https://sqs.us-east-1.amazonaws.com/123456789012/my-queue"
os.environ["DB_HOST"] = "mydb.xxx.us-east-1.rds.amazonaws.com"
os.environ["DB_USER"] = "admin"
os.environ["DB_PASS"] = "password"
os.environ["DB_NAME"] = "appdb"
