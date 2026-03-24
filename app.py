# app.py
from flask import Flask, request, jsonify
import boto3, os, time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from worker import process_task
from db import get_db_conn, init_db

# Initialize DB table
init_db()

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('http_request_latency_seconds', 'Request latency', ['endpoint'])

# AWS clients
s3 = boto3.client('s3', region_name=os.environ.get("AWS_REGION"))
sqs = boto3.client('sqs', region_name=os.environ.get("AWS_REGION"))

app = Flask(__name__)

# -----------------------------
# Upload endpoint
# -----------------------------
@app.route("/upload", methods=["POST"])
def upload_file():
    start = time.time()
    REQUEST_COUNT.labels(method='POST', endpoint='/upload').inc()

    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file provided"}), 400

    try:
        s3.upload_fileobj(file, os.environ.get("S3_BUCKET"), file.filename)
    except Exception as e:
        return jsonify({"error": f"S3 Upload Error: {str(e)}"}), 500

    REQUEST_LATENCY.labels(endpoint='/upload').observe(time.time() - start)
    return jsonify({"message": "File uploaded successfully"}), 200

# -----------------------------
# Queue task endpoint
# -----------------------------
@app.route("/task", methods=["POST"])
def queue_task():
    start = time.time()
    REQUEST_COUNT.labels(method='POST', endpoint='/task').inc()
    data = request.json or {}

    # Insert task into MySQL
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks (task_data) VALUES (%s);", (str(data),))
        task_id = cur.lastrowid
        cur.close()
        conn.close()
    except Exception as e:
        return jsonify({"error": f"DB Error: {str(e)}"}), 500

    # Send to SQS
    try:
        sqs.send_message(
            QueueUrl=os.environ.get("SQS_URL"),
            MessageBody=str({"task_id": task_id, "data": data})
        )
    except Exception as e:
        return jsonify({"error": f"SQS Error: {str(e)}"}), 500

    REQUEST_LATENCY.labels(endpoint='/task').observe(time.time() - start)
    return jsonify({"message": "Task queued", "task_id": task_id}), 200

# -----------------------------
# List tasks endpoint
# -----------------------------
@app.route("/tasks", methods=["GET"])
def list_tasks():
    start = time.time()
    REQUEST_COUNT.labels(method='GET', endpoint='/tasks').inc()

    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, task_data, processed, created_at FROM tasks ORDER BY created_at DESC;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        tasks = [
            {"id": r[0], "data": r[1], "processed": bool(r[2]), "created_at": str(r[3])}
            for r in rows
        ]
    except Exception as e:
        return jsonify({"error": f"DB Error: {str(e)}"}), 500

    REQUEST_LATENCY.labels(endpoint='/tasks').observe(time.time() - start)
    return jsonify({"tasks": tasks}), 200

# -----------------------------
# Health endpoint
# -----------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

# -----------------------------
# Metrics endpoint
# -----------------------------
@app.route("/metrics", methods=["GET"])
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

# -----------------------------
# Run the app
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
