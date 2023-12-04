from aws_cdk import (
    aws_eks as eks,
    aws_iam as iam,
    Stack, CfnOutput
)

from src.modules.ssm_resource.ssm_resource import SSMCustomResource
from constructs import Construct

class EksHelmCharts(Stack):

    def __init__(self, scope: Construct, construct_id: str, eks_cluster: eks.Cluster, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        customresource = SSMCustomResource(self, "SSMResourceStack", ssm_parameter="/platform/account/env")        

        # https://github.com/aws/aws-cdk/issues/24710
        # moving to using the general chart due to issue
        ingress_nginx = eks.HelmChart(
            self,
            "IngressCharts",
            chart="ingress-nginx",
            release="ingress-nginx",
            cluster=eks_cluster,
            namespace="kube-system",
            repository="https://kubernetes.github.io/ingress-nginx",
            values={
                "controller.replicaCount": customresource.result,
                # Add other helm chart values as needed
            },
        )

        # Get Loadbalancer URL
        ingress_service_address = eks.KubernetesObjectValue(self, "LoadBalancerAttribute",
            cluster=eks_cluster,
            object_type="service",
            object_name="ingress-nginx-controller",
            object_namespace="kube-system",
            json_path=".status.loadBalancer.ingress[0].hostname"
        )

        # Store URL in CfnOutput
        CfnOutput(
            self,
            'NginxLoadBalancerUrl',
            value=ingress_service_address.value
        )