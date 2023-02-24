from aws_cdk import (
    Stack,
    aws_autoscaling as autoscaling,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    aws_iam as iam,
    CfnOutput
)

from constructs import Construct

with open("./user_data/user_data.sh") as f:
    user_data = f.read()

ec2_type = "t2.micro"

my_key_pair="abc"

linux_ami = ec2.AmazonLinuxImage(
    generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX,
    edition=ec2.AmazonLinuxEdition.STANDARD,
    virtualization=ec2.AmazonLinuxVirt.HVM,
    storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
    )


class MyTomcatStack(Stack):

    def __init__(self, scope: Construct, construct_id: str,vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
   
        
        # Create Key Pair
        #my_key_pair = ec2.CfnKeyPair(self, 'MyKeyPair',key_name='my-key-pair')
        
        # Create Bastion
        bastion = ec2.BastionHostLinux(
            self,
            "myBastion",
            vpc=vpc,
            subnet_selection=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC),
            instance_name="myBastionHostLinux",
            instance_type=ec2.InstanceType(instance_type_identifier=ec2_type))

        # Setup key_name for bastion host
        bastion.instance.instance.add_property_override("KeyName", my_key_pair)
        
        bastion.connections.allow_from_any_ipv4(ec2.Port.tcp(22), "Internet access SSH")
        
        
        # create security group
        sg = ec2.SecurityGroup(self, "TomcatSecurityGroup",
            vpc=vpc,
            description="Allow inbound traffic to Tomcat instances",
            allow_all_outbound=True
        )
        
        # allow inbound traffic on port 8080 (Tomcat)
        sg.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(8080),
            "Allow Tomcat inbound traffic"
            )
        
        
        # create IAM role for EC2 instances
        role = iam.Role(self, "TomcatRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ReadOnlyAccess")
            ]
        )
        
        
        
        asg = autoscaling.AutoScalingGroup(
            self, 
            "TomcatAutoScalingGroup",
            vpc=vpc,
            instance_type=ec2.InstanceType(instance_type_identifier=ec2_type),
            machine_image=linux_ami,
            role=role,
            security_group=sg,
            user_data=ec2.UserData.custom(user_data),
            desired_capacity=2,
            min_capacity=2,
            max_capacity=4,
            key_name=my_key_pair,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT)
        )
        
        
        
        
        # Create ALB
        alb = elbv2.ApplicationLoadBalancer(
            self,
            "TomcatLoadBalancer",
            vpc=vpc,
            internet_facing=True,
            load_balancer_name="myALB"
        )
        
        # alb.connections.allow_from_any_ipv4(
        #     ec2.Port.tcp(80), "Internet access ALB 80")
        
        listener = alb.add_listener("TomcatHTTPListener",
            port=80,
            open=True
        )
        
        
        
        # sg.add_ingress_rule(
        #     ec2.Peer.any_ipv4(),
        #     ec2.Port.tcp(22),
        #     "Allow Tomcat inbound SSH"
        #     )
        
        # create EC2 instance using Amazon Linux 2 AMI
        
        
        listener.add_targets(
            "TomcatTargetGroup",
            port=8080,
            targets=[asg],
        )

        CfnOutput(self, "TomcatLoadBalancerDNS",
            value=alb.load_balancer_dns_name,
            description="Tomcat Load Balancer DNS name"
        )