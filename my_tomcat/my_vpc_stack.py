from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    CfnOutput
)

from constructs import Construct

class MyVpcStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
       # create VPC
        self.vpc = ec2.Vpc(
            self,
            "MyVPC",
            cidr="10.0.0.0/16",
            max_azs=2,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT,
                    cidr_mask=24
                )
            ]
        )
        CfnOutput(self, "Output",
                       value=self.vpc.vpc_id)