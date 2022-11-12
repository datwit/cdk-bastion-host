#!/usr/bin/env python3

import aws_cdk as cdk

from cdk_bastion_host.cdk_bastion_host_stack import CdkBastionHostStack


app = cdk.App()
CdkBastionHostStack(app, "cdk-bastion-host")

app.synth()
