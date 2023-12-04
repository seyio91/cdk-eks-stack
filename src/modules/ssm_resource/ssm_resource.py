from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_ssm as ssm,
    aws_iam as iam,
    CustomResource,
    Token,
)
from constructs import Construct

class SSMCustomResource(Stack):

    def __init__(self, scope: Construct, construct_id: str, ssm_parameter: ssm.StringParameter, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Lambda Function IAM Role
        lambdarole = iam.Role(
            scope, "LambdaIAMRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        )

        # Attach Permissoins to Lambda Role
        lambdarole.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))
        lambdarole.add_to_policy(
            iam.PolicyStatement(
                actions=["ssm:GetParameter"],
                resources=["*"]
            )
        )

        # Create Lambda Function
        lambda_function = _lambda.Function(
            scope, 'IndexHandler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.from_asset("./src/modules/ssm_resource/lambdas"),
            handler='ssm_lambda.handler',
            role=lambdarole
        )

        lambda_function.node.add_dependency(lambdarole)


        # Create Custom Resource
        resource = CustomResource(scope, "SSMResouce",
            resource_type="Custom::SSMCustomResource",
            service_token=lambda_function.function_arn,
            properties={
                "Name": ssm_parameter
            }
        )

        resource.node.add_dependency(lambda_function)

        # Set Custom Resource Attribyte
        self.result = Token.as_string(resource.get_att("ParameterValue"))
