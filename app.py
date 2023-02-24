#!/usr/bin/env python3
import os

import aws_cdk as cdk

from my_tomcat.my_tomcat_stack import MyTomcatStack
from my_tomcat.my_vpc_stack import MyVpcStack
# from my_tomcat.my_acm_stack import MyVpcStack

app = cdk.App()

vpc_stack = MyVpcStack(app, "My-vpc")

MyTomcatStack(app, "MyTomcatStack",vpc=vpc_stack.vpc)

app.synth()
