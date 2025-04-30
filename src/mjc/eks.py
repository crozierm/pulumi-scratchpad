import json

import pulumi
import pulumi_aws as aws


# WIP from AI code

def create_eks_cluster(cluster_name,
                       desired_capacity,
                       min_size,
                       max_size,
                       instance_type,
                       subnet_ids,
                       version="1.32"):
    eks_role = create_eks_role(cluster_name)

    node_group_role = create_node_group_role(cluster_name)

    eks_cluster = aws.eks.Cluster(
        cluster_name,
        role_arn=eks_role.arn,
        version=version,
        vpc_config={
            "subnetIds": subnet_ids
        }
    )

    node_group = aws.eks.NodeGroup(
        f"{cluster_name}-node-group",
        cluster_name=eks_cluster.name,
        node_role_arn=node_group_role.arn,
        subnet_ids=subnet_ids,
        scaling_config={
            "desiredSize": desired_capacity,
            "minSize": min_size,
            "maxSize": max_size,
        },
        instance_types=[instance_type]
    )
    # ClaudeGPT generated this. It seems trashy AF.
    kubeconfig = pulumi.Output.all(eks_cluster.endpoint, eks_cluster.certificate_authority, eks_cluster.name).apply(
        lambda args: f"""
    apiVersion: v1
    clusters:
    - cluster:
        server: {args[0]}
        certificate-authority-data: {args[1]['data']}
      name: {args[2]}
    contexts:
    - context:
        cluster: {args[2]}
      name: {args[2]}
    current-context: {args[2]}
    kind: Config
    preferences: {{}}
    users:
    - name: {args[2]}
    """
    )
    pulumi.export("kubeconfig", kubeconfig)
    pulumi.export("cluster_name", eks_cluster.name)


def create_node_group_role(cluster_name):
    # Create Node Group IAM Role
    node_group_role = aws.iam.Role(
        f"{cluster_name}-node-group-role",
        assume_role_policy=json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Principal": {
                            "Service": "ec2.amazonaws.com"
                        },
                        "Effect": "Allow"
                    }
                ]
            })
    )
    # Attach the AmazonEKSWorkerNodePolicy to the node group role
    worker_node_policy = aws.iam.RolePolicyAttachment(
        f"{cluster_name}-node-instance-policy-attachment",
        role=node_group_role.name,
        policy_arn="arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
    )
    # Attach additional policies required for EKS workers
    cni_policy_attachment = aws.iam.RolePolicyAttachment(
        f"{cluster_name}-node-cni-policy-attachment",
        role=node_group_role.name,
        policy_arn="arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
    )
    ec2_policy_attachment = aws.iam.RolePolicyAttachment(
        f"{cluster_name}-node-ec2-policy-attachment",
        role=node_group_role.name,
        policy_arn="arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
    )
    # Create EC2 Instance Profile
    instance_profile = aws.iam.InstanceProfile(
        f"{cluster_name}-node-instance-profile",
        role=node_group_role.name
    )
    return node_group_role


def create_eks_role(cluster_name):
    eks_role = aws.iam.Role(
        f"{cluster_name}-eks-role",
        assume_role_policy=json.dumps(
            {"Version": "2012-10-17",
             "Statement": [
                 {
                     "Action": "sts:AssumeRole",
                     "Principal": {
                         "Service": "eks.amazonaws.com"
                     },
                     "Effect": "Allow"
                 }
             ]
             })
    )
    # Attach the AmazonEKSClusterPolicy to the cluster role
    cluster_policy_attachment = aws.iam.RolePolicyAttachment(
        f"{cluster_name}-eks-cluster-policy-attachment",
        role=eks_role.name,
        policy_arn="arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
    )
    # Attach the AmazonEKSServicePolicy to the cluster role
    service_policy_attachment = aws.iam.RolePolicyAttachment(
        f"{cluster_name}-eks-service-policy-attachment",
        role=eks_role.name,
        policy_arn="arn:aws:iam::aws:policy/AmazonEKSServicePolicy"
    )
    return eks_role
