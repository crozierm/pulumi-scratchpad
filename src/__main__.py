from pulumi_kubernetes.core.v1 import Namespace

from mjc import vpc
from mjc.common_security_groups import declare_bastion_sg
from mjc.ec2 import declare_ubuntu_ec2
from mjc.eks import create_eks_cluster
from mjc.eks_host import create_ubuntu_container
from mjc.vpc import declare_vpc_and_subnets


def main():
    prefix = "mjc1"
    region = "us-west-2"

    vpcinf: vpc.VPCInfo = declare_vpc_and_subnets(prefix, region)

    bastion_security_group = declare_bastion_sg(vpcinf.vpc.id)
    pub_ec2 = declare_ubuntu_ec2("bastion", "crozierm_home", vpcinf.public_subnets[0].id, [bastion_security_group])
    private_ec2 = declare_ubuntu_ec2("private_host", "crozierm_home", vpcinf.private_subnets[0].id, [bastion_security_group])

    create_eks_cluster(cluster_name=region,
                       desired_capacity=2,
                       min_size=1,
                       max_size=3,
                       instance_type="t3.medium",
                       subnet_ids=vpcinf.private_subnets)

    kafka_namespace = Namespace(
        "kafka-namespace1",
        metadata={
            "name": "kafka1",
        },
    )

    # create_strimzi_kafka_cluster(kafka_namespace)
    create_ubuntu_container(kafka_namespace)


if __name__ == "__main__":
    main()
