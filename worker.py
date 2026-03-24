# worker.py
import boto3
import os
import time
from db import get_db_conn

# AWS SQS client
sqs = boto3.client('sqs', region_name=os.environ.get("AWS_REGION"))

def process_task():
    queue_url = os.environ.get("SQS_URL")
    print("Worker started, polling SQS...")

    while True:
        try:
            resp = sqs.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=5
            )
            messages = resp.get('Messages', [])

            if not messages:
                continue  # nothing to process

            for msg in messages:
                task_info = eval(msg['Body'])  # {"task_id": 123, "data": {...}}
                task_id = task_info.get("task_id")
                data = task_info.get("data")

                print(f"Processing task ID: {task_id}, data: {data}")
                
                # Simulate task processing time
                time.sleep(1)

                # Update task as processed in MySQL
                try:
                    conn = get_db_conn()
                    cur = conn.cursor()
                    cur.execute("UPDATE tasks SET processed = TRUE WHERE id = %s;", (task_id,))
                    cur.close()
                    conn.close()
                    print(f"Task {task_id} marked as processed in DB")
                except Exception as e:
                    print(f"DB Error updating task {task_id}: {str(e)}")

                # Delete message from SQS
                try:
                    sqs.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=msg['ReceiptHandle']
                    )
                    print(f"Task {task_id} deleted from SQS")
                except Exception as e:
                    print(f"SQS Error deleting task {task_id}: {str(e)}")

        except Exception as e:
            print(f"Worker encountered error: {str(e)}")
            time.sleep(5)  # backoff if something goes wrong

# Entry point for running directly
if __name__ == "__main__":
    process_task()
