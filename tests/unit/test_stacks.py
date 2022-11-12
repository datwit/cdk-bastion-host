import aws_cdk as core
import aws_cdk.assertions as assertions
from stacks.vpc_stack import VPCStack
from stacks.neptune_stack import NeptuneStack

def test_vpc_created():
    app = core.App()
    stack = VPCStack(app, "cdk-bastion-host")
    template = assertions.Template.from_stack(stack)

    template.resource_count_is("AWS::EC2::VPC", 1)

def test_neptune_cluster_created():
    app = core.App()
    vpc_stack = VPCStack(app, 'bastion-and-vpc')
    stack = NeptuneStack(app, 'db-cluster', vpc=vpc_stack.vpc)

    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::Neptune::DBCluster", 1)