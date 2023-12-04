import boto3
import json
import urllib3

SUCCESS = 'SUCCESS'
FAILED = 'FAILED'

HTTP = urllib3.PoolManager()

def handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    request_type = event['RequestType']
    try:

        if request_type == 'Delete': 
            send_response(event, context, SUCCESS)
        else:
            data = get_ssm_parameter(event)
            send_response(event, context, SUCCESS, data)
    except Exception as e:
        print('Function failed due to exception.')
        print(e)
        send_response(event, context, FAILED)
    return 'Complete'

def get_ssm_parameter(event):
    ssm_client = boto3.client("ssm", region_name='eu-west-1')
    parameter_name = event["ResourceProperties"]["Name"]
    response = ssm_client.get_parameter(Name=parameter_name, WithDecryption=True)
    parameter_value = response["Parameter"]["Value"]

    if parameter_value == "development":
        replicaCount = 1
    else:
        replicaCount = 2

    data = {
        "ParameterValue": replicaCount
    }
    return data
    

def send_response(event, context, response_status, response_data=None):
    response_url = event['ResponseURL']
    responseBody = {
        'Status' : response_status,
        'Reason' : f'See the details in CloudWatch Log Stream: {context.log_stream_name}',
        'PhysicalResourceId' : context.log_stream_name,
        'StackId' : event['StackId'],
        'RequestId' : event['RequestId'],
        'LogicalResourceId' : event['LogicalResourceId'],
        'NoEcho' : True,
        'Data' : response_data
    }
    json_response_body = json.dumps(responseBody)
    headers = {
        'content-type' : '',
        'content-length' : str(len(json_response_body))
    }
    try:
        response = HTTP.request('PUT',  response_url, headers=headers, body=json_response_body)
        print(f'Status code: {response.status}')
    except Exception as e:
        print("send(..) failed executing http.request(..):", e)