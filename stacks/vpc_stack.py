from aws_cdk import (
    CfnOutput,
    Stack,
    aws_ec2 as ec2
)
from constructs import Construct


class VPCStack(Stack):
    vpc: ec2.Vpc
    bastionSG: ec2.SecurityGroup

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.vpc = ec2.Vpc(
            self,
            'VPC',
            ip_addresses=ec2.IpAddresses.cidr('10.0.0.0/16'),
            nat_gateways=1,
            max_azs=3,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name='private-subnet',
                    cidr_mask=24,
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
                ),
                ec2.SubnetConfiguration(
                    name='public-subnet',
                    cidr_mask=24,
                    subnet_type=ec2.SubnetType.PUBLIC
                ),
                ec2.SubnetConfiguration(
                    name='isolate-subnet',
                    cidr_mask=28,
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
                ),
            ]
        )

        self.bastionSG = ec2.SecurityGroup(
            self,
            'bastion-sg',
            description='Security group for the bastion, no inbound open '
                        'because we should access to the bastion via AWS SSM',
            vpc=self.vpc,
            allow_all_outbound=True
        )

        bastion = ec2.BastionHostLinux(
            self, 'SecureBastion',
            vpc=self.vpc,
            instance_name='secure-bastion',
            subnet_selection=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC
            ),
            security_group=self.bastionSG,
        )
        bastion.allow_ssh_access_from(ec2.Peer.any_ipv4())
        CfnOutput(self, 'secure-bastion-id', value=bastion.instance_id)
        CfnOutput(
            self, 'secure-bastion-dns-name',
            value=bastion.instance.instance_public_dns_name
        )
        CfnOutput(
            self, 'secure-bastion-zone',
            value=bastion.instance.instance_availability_zone
        )
