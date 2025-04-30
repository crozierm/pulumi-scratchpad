import pulumi
import pulumi_aws as aws


def declare_ubuntu_ec2(hostname: str,
                       key_name: str,
                       subnet_id: pulumi.output.Output[str],
                       security_group_ids: list[aws.ec2.SecurityGroup],
                       instance_type="t2.micro"):
    ubuntu_ami = aws.ec2.get_ami(
        most_recent=True,
        owners=["099720109477"],  # Canonical's AWS account ID for Ubuntu
        filters=[
            {"name": "name", "values": ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]},
            {"name": "virtualization-type", "values": ["hvm"]},
        ],
    )

    ec2_instance = aws.ec2.Instance(
        hostname,
        ami=ubuntu_ami.id,
        instance_type=instance_type,
        subnet_id=subnet_id,
        vpc_security_group_ids=security_group_ids,
        key_name=key_name
    )

    pulumi.export(f"{hostname}_public_ip", ec2_instance.public_ip)
    pulumi.export(f"{hostname}_private_ip", ec2_instance.private_ip)
    pulumi.export(f"{hostname}_public_dns", ec2_instance.public_dns)
