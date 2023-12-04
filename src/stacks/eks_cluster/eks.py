from aws_cdk import (
    aws_eks as eks,
    aws_ec2 as ec2,
    aws_iam as iam,
    lambda_layer_kubectl_v26 as lykubectl,
    Stack, CfnOutput
)
from constructs import Construct

class EksCluster(Stack):

    def __init__(self, scope: Construct, construct_id: str, stage: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        region = self.region
        availability_zones = [f'{region}a', f'{region}b']
        # Create a new VPC
        vpc = ec2.Vpc(self, 'Vpc',
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
            vpc_name=f'eks-{stage}-1-26-vpc',
            enable_dns_hostnames=True,
            enable_dns_support=True,
            availability_zones=availability_zones,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name=f'eks-{stage}-1-26-subnet-public',
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name=f'eks-{stage}-1-26-subnet-private',
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                )
            ]
        )
        # Add an S3 VPC endpoint
        vpc.add_gateway_endpoint('S3Endpoint',
                                 service=ec2.GatewayVpcEndpointAwsService.S3)

        # IAM Role for Helm/Kubectl Lambda
        lambda_role = iam.Role(
            self,
            'EksLambdaRole',
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )

        lambda_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryReadOnly"))
        lambda_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))

        # IAM Policies Needed to Authenticate With Public ECR
        lambda_role_policy = iam.PolicyStatement(
            actions=[
                'ecr-public:GetAuthorizationToken',
                'sts:GetServiceBearerToken',
                'ecr-public:BatchCheckLayerAvailability',
                'ecr-public:GetRepositoryPolicy',
                'ecr-public:DescribeRepositories',
                'ecr-public:DescribeRegistries',
                'ecr-public:DescribeImages',
                'ecr-public:DescribeImageTags',
                'ecr-public:GetRepositoryCatalogData',
                'ecr-public:GetRegistryCatalogData'
            ],
            resources=['*'],
        )
        lambda_role.add_to_policy(lambda_role_policy)

        kubectl_layer = lykubectl.KubectlV26Layer(self, 'KubectlV26Layer')

        # Create EKS Cluster
        cluster = eks.Cluster(self, "MyCluster",
                        cluster_name=f'eks-{stage}-1-26-cluster',
                        version=eks.KubernetesVersion.V1_26,
                        vpc=vpc,
                        default_capacity=0,
                        kubectl_layer=kubectl_layer,
                        kubectl_lambda_role=lambda_role,
                    )
        
        cluster.aws_auth.add_masters_role(lambda_role)


        # Master IAM Role for Cluster Access
        masters_role = iam.Role(
            self,
            'EksMastersRole',
            assumed_by=iam.AccountRootPrincipal()
        )

        master_role_policy = iam.PolicyStatement(
            actions=['eks:DescribeCluster'],
            resources=['*'],  
        )
        masters_role.add_to_policy(master_role_policy)

        cluster.aws_auth.add_masters_role(masters_role)

        # Create the EC2 node group
        nodegroup = cluster.add_nodegroup_capacity(
            'Nodegroup',
            instance_types=[ec2.InstanceType('t3.medium')],
            desired_size=1,
            min_size=1,
            max_size=2,
            ami_type=eks.NodegroupAmiType.AL2_X86_64
        )

        provider = eks.OpenIdConnectProvider(self, "Provider",
            url=cluster.cluster_open_id_connect_issuer_url,
        )

        # Output the EKS cluster name
        CfnOutput(
            self,
            'ClusterNameOutput',
            value=cluster.cluster_name,
        )

        # Output the EKS master role ARN
        CfnOutput(
            self,
            'ClusterMasterRoleOutput',
            value=masters_role.role_arn
        )

        self.cluster = cluster
