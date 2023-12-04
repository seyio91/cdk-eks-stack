from aws_cdk import (
    Stack,
    aws_ssm as ssm
)
from constructs import Construct
from enum import Enum

class EnvironmentType(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class SSMPlatformParameter(Stack):

    def __init__(self, scope: Construct, construct_id: str, ssm_parameter: ssm.StringParameter, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.validate_enum_value(EnvironmentType, ssm_parameter)
        param = ssm.StringParameter(
            self,
            "PlatformParameter",
            parameter_name="/platform/account/env",
            string_value=ssm_parameter,
        )

    def validate_enum_value(self, enum_type, value):
        if value not in [e.value for e in enum_type]:
            raise ValueError(f"Invalid value '{value}' for {enum_type.__name__}. Allowed values are {enum_type._member_names_}.")
