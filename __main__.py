import pulumi
import pulumi_aws as aws

# Create a new EC2 key pair

# Create a VPC to launch our instances into
vpc = aws.ec2.Vpc("custom",
                  cidr_block="172.16.0.0/16")

# Create an internet gateway and attach it to our VPC
ig = aws.ec2.InternetGateway("ig",
                             vpc_id=vpc.id)

# Create a route table that has a route to the internet gateway
rt = aws.ec2.RouteTable("rt",
                        routes=[{
                            "cidr_block": "0.0.0.0/0",
                            "gateway_id": ig.id
                        }],
                        vpc_id=vpc.id)

# Create a subnet and associate our route table to it
subnet = aws.ec2.Subnet("subnet",
                        vpc_id=vpc.id,
                        cidr_block="172.16.10.0/24",
                        map_public_ip_on_launch=True,
                        availability_zone="eu-central-1a")
rta = aws.ec2.RouteTableAssociation("rta",
                                    route_table_id=rt.id,
                                    subnet_id=subnet.id)

# Create a security group that allows ssh and all egress traffic
sg = aws.ec2.SecurityGroup("pulumi-sg",
                           vpc_id=vpc.id,
                           egress=[{
                               "protocol": "-1",
                               "from_port": 0,
                               "to_port": 0,
                               "cidr_blocks": ["0.0.0.0/0"],
                           }],
                           ingress=[{
                               "protocol": "tcp",
                               "from_port": 80,
                               "to_port": 80,
                               "cidr_blocks": ["0.0.0.0/0"],
                           }])

# Userdata to boot python Docker image
user_data = """#!/bin/bash
            sudo yum update -y
              sudo yum install docker -y
              service docker start
              usermod -a -G docker ec2-user
              chkconfig docker on
              docker pull stefanprodan/podinfo
              docker run -d -p 80:9898 stefanprodan/podinfo"""

              # Create a new instance
instance = aws.ec2.Instance("instance",
                            ami="ami-0f7204385566b32d0",  # us-west-2 Amazon Linux 2 AMI
                            instance_type="t2.micro",
                            subnet_id=subnet.id,
                            vpc_security_group_ids=[sg.id],  # reference security group
                            user_data=user_data  # boot python docker image
                            )
