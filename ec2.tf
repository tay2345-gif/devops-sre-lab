resource "aws_instance" "app_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.ec2_instance_type
  subnet_id              = aws_subnet.public.id
  security_groups        = [aws_security_group.ec2_sg.name]
  iam_instance_profile   = aws_iam_instance_profile.ec2_profile.name
  associate_public_ip_address = true
  key_name               = var.key_name

  user_data = <<-EOF
              #!/bin/bash
              sudo apt update
              sudo apt install -y python3-pip
              pip3 install flask boto3 prometheus_client mysql-connector-python
              # Pull your app from GitHub (replace with your repo)
              git clone https://github.com/yourusername/your-repo.git /home/ubuntu/app
              cd /home/ubuntu/app
              python3 app.py &
              python3 worker.py &
              EOF
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }
}