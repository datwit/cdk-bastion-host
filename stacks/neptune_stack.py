from aws_cdk import (
    CfnOutput,
    RemovalPolicy,
    Stack,
    RemovalPolicy,
    aws_ec2 as ec2,
    aws_logs as logs,
    aws_neptune_alpha as neptune
)
from constructs import Construct


class NeptuneStack(Stack):

    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            vpc: ec2.Vpc,
            **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        cluster_parameter_group = neptune.ClusterParameterGroup(
            self, "NeptuneClusterParams",
            description="Cluster parameter group",
            parameters={
                "neptune_enable_audit_log": "1"
            }
        )
        cluster = neptune.DatabaseCluster(
            self,
            "NeptuneDatabase",
            vpc=vpc,
            instance_type=neptune.InstanceType.T3_MEDIUM,
            auto_minor_version_upgrade=True,
            cluster_parameter_group=cluster_parameter_group,
            cloudwatch_logs_exports=[neptune.LogType.AUDIT],
            cloudwatch_logs_retention=logs.RetentionDays.FIVE_DAYS,
            removal_policy=RemovalPolicy.DESTROY
        )
        cluster.connections.allow_default_port_from_any_ipv4()
        neptune_endpoint = cluster.cluster_endpoint.socket_address

        CfnOutput(self, "neptune_endpoint", value=neptune_endpoint)
