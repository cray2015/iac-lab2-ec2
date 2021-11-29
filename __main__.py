"""An AWS Python Pulumi program"""

import pulumi
import pulumi_aws as aws


config = pulumi.Config()
ec2_key_name = config.require("ec2_key_name")

ami = aws.ec2.get_ami(
    most_recent=True,
    owners=[
        "099720109477"
    ],
    filters=[
        {
            "name": "name",
            "values": [
                "ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"
            ]
        }
    ]
)

vpc = aws.ec2.get_vpc(default=True)

security_group = aws.ec2.SecurityGroup(
    "web-secgrp",
    description='Enable HTTP access',
    ingress=[
        {
            'protocol': 'tcp',
            'from_port': 80,
            'to_port': 80,
            'cidr_blocks': ['0.0.0.0/0']
        },
        {
            'protocol': 'tcp',
            'from_port': 22,
            'to_port': 22,
            'cidr_blocks': ['0.0.0.0/0']
        },
    ],
    egress=[
        # {
        #     'protocol': 'tcp',
        #     'from_port': 80,
        #     'to_port': 80,
        #     'cidr_blocks': ['0.0.0.0/0']
        # },
        {
            'protocol': "ALL",
            'from_port': 0,
            'to_port': 0,
            'cidr_blocks': ['0.0.0.0/0']
        },
    ]
)

common_tags = {
    "Name": "pulumi_made",
    "created_by": "vibhs",
    "env": pulumi.get_stack(),
    "description": "simple instance created by pulumi CLI",
    "region": config.get("aws:region")
}

ebs_root_device = aws.ec2.InstanceEbsBlockDeviceArgs(
    delete_on_termination=True,
    volume_size=10,
    device_name="/dev/sda1"
)

server = aws.ec2.Instance(
    "pulumi_made",
    ami=ami.id,
    vpc_security_group_ids=[security_group.id],
    instance_type="t2.micro",
    tags=common_tags,
    key_name=ec2_key_name,
    # availability_zone="us-east-1a",
    ebs_block_devices=[ebs_root_device],
    volume_tags=common_tags,

)

# EBS size
# key pair attach

pulumi.export("ip", server.public_ip)
pulumi.export("hostname", server.public_dns)
