output "ec2_public_ip" {
  value = aws_instance.app_server.public_ip
}

output "rds_endpoint" {
  value = aws_db_instance.mysql.endpoint
}

output "s3_bucket" {
  value = aws_s3_bucket.app_bucket.bucket
}

output "sqs_url" {
  value = aws_sqs_queue.task_queue.id
}