import dataclasses

import pulumi
import pulumi_aws as aws

'''
What  do I want?
* VPC
* four subnets in two AZs
* two pub, two private
* NAT GW in privates
* IGW in publics

'''


@dataclasses.dataclass
class VPCInfo:
    vpc: aws.ec2.Vpc
    igw: aws.ec2.InternetGateway
    public_subnets: list[aws.ec2.Subnet]
    private_subnets: list[aws.ec2.Subnet]


def declare_vpc_and_subnets(prefix,
                            region="us-west-2",  # this could be inferred?
                            vpc_cidr="10.0.0.0/16",
                            public_subnets: list[str] = ["10.0.0.0/24", "10.0.1.0/24"],
                            private_subnets: list[str] = ["10.0.4.0/22", "10.0.8.0/22"],
                            azs: list[str] = ["a", "b"]):
    igw, vpc, route_table = declare_vpc(prefix, vpc_cidr)

    public_subnets = [declare_public_subnets(prefix, cidr_block, region, az, vpc, route_table) for cidr_block, az in
                      zip(public_subnets, azs)]

    private_subnets = [declare_private_subnet(prefix, cidr, region, az, natgw_subnet, vpc) for cidr, az, natgw_subnet in
                       zip(private_subnets, azs, public_subnets)]

    pulumi.export("vpc_id", vpc.id)
    return VPCInfo(vpc, igw, public_subnets, private_subnets)


def declare_vpc(prefix: str,
                vpc_cidr: str) -> tuple[aws.ec2.InternetGateway, aws.ec2.Vpc, aws.ec2.RouteTable]:
    vpc = aws.ec2.Vpc(f"{prefix}-vpc",
                      cidr_block=vpc_cidr,
                      enable_dns_support=True,
                      enable_dns_hostnames=True)
    igw = aws.ec2.InternetGateway(f"{prefix}-igw",
                                  vpc_id=vpc.id)
    route_table = aws.ec2.RouteTable(f"{prefix}-route-table",
                                     vpc_id=vpc.id,
                                     routes=[
                                         {
                                             "cidr_block": "0.0.0.0/0",
                                             "gateway_id": igw.id
                                         },
                                     ])
    return igw, vpc, route_table


def declare_public_subnets(prefix: str,
                           cidr_block: str,
                           region: str,
                           az: str,
                           vpc: aws.ec2.Vpc,
                           public_route_table) -> aws.ec2.Subnet:
    pub_subnet_az = aws.ec2.Subnet(f"{prefix}-public-subnet-{az}",
                                   vpc_id=vpc.id,
                                   cidr_block=cidr_block,
                                   map_public_ip_on_launch=True,
                                   availability_zone=f"{region}-{az}")

    _route_table_association_az1 = aws.ec2.RouteTableAssociation(f"{prefix}-public-route-table-association-{az}",
                                                                 subnet_id=pub_subnet_az.id,
                                                                 route_table_id=public_route_table.id)
    return pub_subnet_az


def declare_private_subnet(prefix: str,
                           cidr: str,
                           region: str,
                           az: str,
                           natgw_public_subnet,
                           vpc: aws.ec2.Vpc) -> aws.ec2.Subnet:
    private_subnet = aws.ec2.Subnet(f"{prefix}-private-subnet-{az}",
                                    vpc_id=vpc.id,
                                    cidr_block=cidr,
                                    map_public_ip_on_launch=False,
                                    availability_zone=f"{region}-{az}")

    # Create NAT Gateways in az1 and az2
    private_nat_eip = aws.ec2.Eip(f"{prefix}-private-nat-eip-{az}", domain="vpc")
    nat_gateway = aws.ec2.NatGateway(f"{prefix}-private-nat-gateway-{az}",
                                     allocation_id=private_nat_eip.id,
                                     subnet_id=natgw_public_subnet.id)
    private_route_table = aws.ec2.RouteTable(f"{prefix}-private-route-table-{az}",
                                             vpc_id=vpc.id,
                                             routes=[
                                                 {"cidr_block": "0.0.0.0/0", "nat_gateway_id": nat_gateway.id},
                                             ])
    _private_route_table_association_az = aws.ec2.RouteTableAssociation(f"{prefix}-private-route-table-association-{az}",
                                                                         subnet_id=private_subnet.id,
                                                                         route_table_id=private_route_table.id)
    return private_subnet
