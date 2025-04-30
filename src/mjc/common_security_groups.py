import pulumi
import pulumi_aws as aws

config = pulumi.Config()
home_ip = config.require("home_ip")  # Question: can config values be lists? Find out!


def declare_bastion_sg(vpc_id) -> aws.ec2.SecurityGroup:
    bastion_ssh_sg = aws.ec2.SecurityGroup(
        'home-ssh-security-group2',
        vpc_id=vpc_id,
        description="Allow SSH from Home",
        ingress=[
            aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=22,
                to_port=22,
                cidr_blocks=[f"{home_ip}/32"],
            ),
            aws.ec2.SecurityGroupIngressArgs(
                protocol="-1",
                from_port=0,
                to_port=0,
                cidr_blocks=[f"10.0.0.0/16"],
            )
        ],
        egress=[
            aws.ec2.SecurityGroupEgressArgs(
                protocol="-1",
                from_port=0,
                to_port=0,
                cidr_blocks=["0.0.0.0/0"],
            ),
        ],
    )
    return bastion_ssh_sg
