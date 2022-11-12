#!/usr/bin/env python3

import aws_cdk as cdk

from stacks.vpc_stack import VPCStack
from stacks.neptune_stack import NeptuneStack

app = cdk.App()
vpc_stack = VPCStack(app, "BastionStack")
NeptuneStack(app, "NeptuneStack", vpc=vpc_stack.vpc)

app.synth()
