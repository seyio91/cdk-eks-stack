#!/usr/bin/env python3
import os
import aws_cdk as cdk

from src.stacks.ssm_store.ssm_add import SSMPlatformParameter
from src.stacks.eks_cluster.eks import EksCluster
from src.stacks.eks_charts.charts import EksHelmCharts

stage="development"

app = cdk.App()

platform_parameter = SSMPlatformParameter(app, "SSMPlatformParameterStack", ssm_parameter=stage)
eks_platform_cluster = EksCluster(app, "EksClusterStack", stage=stage)
eks_helm_charts = EksHelmCharts(app, "EksHelmChartsStack", eks_cluster=eks_platform_cluster.cluster)

# Tags
cdk.Tags.of(eks_platform_cluster).add("Stack", "EksClusterStack")
cdk.Tags.of(platform_parameter).add("Stack", "SSMPlatformParameterStack")
cdk.Tags.of(eks_helm_charts).add("Stack", "EksHelmChartsStack")

eks_helm_charts.add_dependency(platform_parameter)

app.synth()
