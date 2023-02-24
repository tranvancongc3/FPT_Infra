from aws_cdk import (
    Stack,
    CfnOutput,
    aws_acmpca as acmpca,
    aws_certificatemanager as acm,
    aws_route53 as route53,
)


class MyTomcatStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        private_ca = acmpca.CfnCertificateAuthority(
            self, 'PrivateCA2',
            type='ROOT',
            key_algorithm='RSA_2048',
            signing_algorithm='SHA256WITHRSA',
            subject={
                'country': 'VietNam',
                'state': 'Washington',
                'organization': 'MyOrg',
                'organizational_unit': 'IT'
                },
            revocation_configuration={
                'crl_configuration': {
                    'enabled': True,
                    'expiration_in_days': 30,
                    'custom_cname': 'my-custom-crl-cname.travacong1.com'
                    }
                },
        )
        
        
        zone = route53.HostedZone(self, "HostedZone",
            zone_name="travacong1.com",
            comment="Private Hosted Zone",
        )
        
        private_cert = acm.Certificate(
            self, 'MyCertificate',
            domain_name='b.travacong1.com',
            validation =acm.CertificateValidation.from_dns(zone),
            )
        
        