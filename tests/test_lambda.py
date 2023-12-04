from src.modules.ssm_resource.lambdas.ssm_lambda import get_ssm_parameter
import boto3
import pytest



@pytest.fixture(autouse=True)
def put_parameter(request):
    marker = request.node.get_closest_marker("environment")
    data = marker.args[0]

    client = boto3.client('ssm', region_name="eu-west-1")

    parameter_name = "/platform/account/test_env"
    client.put_parameter(
        Name=parameter_name,
        Value=data,
        Type='String'
    )

    yield parameter_name

    # cleanup
    client.delete_parameter(
        Name=parameter_name
    )
    
@pytest.mark.environment("development")
def test_development_replicas(put_parameter):
    event = {
        "ResourceProperties": {
            "Name": put_parameter
        }
    }
    data = get_ssm_parameter(event)
    assert data["ParameterValue"] == 1

@pytest.mark.environment("staging")
def test_staging_replicas(put_parameter):
    event = {
        "ResourceProperties": {
            "Name": put_parameter
        }
    }
    data = get_ssm_parameter(event)
    assert data["ParameterValue"] == 2

@pytest.mark.environment("production")
def test_production_replicas(put_parameter):
    event = {
        "ResourceProperties": {
            "Name": put_parameter
        }
    }
    data = get_ssm_parameter(event)
    assert data["ParameterValue"] == 2