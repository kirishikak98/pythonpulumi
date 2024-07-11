import pulumi
import pulumi_aws as aws

# Define the existing key pair name
key_pair_name = "awsmy"  # Replace with your key pair name

# Define instance type
size = 't3.micro'

# Get the latest Ubuntu 20.04 LTS AMI
ami = aws.ec2.get_ami(most_recent=True,
                      owners=["099720109477"],  # Canonical
                      filters=[{"name": "name", "values": ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]}])

# Create a security group allowing HTTP, SSH, and custom Flask port access
group = aws.ec2.SecurityGroup('webserver-secgrp',
    description='Enable HTTP, SSH, and Flask app access',
    ingress=[
        {'protocol': 'tcp', 'from_port': 22, 'to_port': 22, 'cidr_blocks': ['0.0.0.0/0']},  # SSH access
        {'protocol': 'tcp', 'from_port': 80, 'to_port': 80, 'cidr_blocks': ['0.0.0.0/0']},  # HTTP access
        {'protocol': 'tcp', 'from_port': 5000, 'to_port': 5000, 'cidr_blocks': ['0.0.0.0/0']}  # Flask app access
    ],
    egress=[
        {'protocol': '-1', 'from_port': 0, 'to_port': 0, 'cidr_blocks': ['0.0.0.0/0']}  # Allow all outbound traffic
    ]
)

# User data script to set up and run the Flask application
user_data = """#!/bin/bash
sudo apt-get update -y
apt install python3-pip -y
sudo apt-get install -y python3-venv git

# Clone the repository
git clone https://github.com/JasonHaley/hello-python.git /home/ubuntu/hello-python

# Create and activate virtual environment
cd /home/ubuntu/hello-python
python3 -m venv venv
source venv/bin/activate

# Install dependencies
cd app
pip install -r requirements.txt

# Run the Flask application with nohup
nohup python3 main.py 
"""

# Create an EC2 instance with the user data script
server = aws.ec2.Instance('webserver-www',
    instance_type=size,
    vpc_security_group_ids=[group.id],
    ami=ami.id,
    user_data=user_data,
    tags={
        "Name": "webserver-www",
    })

# Export the public IP and DNS of the instance
pulumi.export('publicIp', server.public_ip)
pulumi.export('publicHostName', server.public_dns)
