variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "vpc_cidr" {
  default = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  default = "10.0.1.0/24"
}

variable "private_subnet_cidr" {
  default = "10.0.2.0/24"
}

variable "ec2_instance_type" {
  default = "t3.medium"
}

variable "db_username" {
  default = "admin"
}

variable "db_password" {
  description = "Strong password for RDS"
  type        = string
  sensitive   = true
}

variable "key_name" {
  description = "Name of the key pair to use for EC2 instances"
  type        = string
}