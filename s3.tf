resource "aws_s3_bucket" "app_bucket" {
  bucket = "my-app-bucket-${random_id.bucket_id.hex}"
}

resource "random_id" "bucket_id" {
  byte_length = 4
}
