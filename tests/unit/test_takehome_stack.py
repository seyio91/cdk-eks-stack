import aws_cdk as core
import aws_cdk.assertions as assertions

from takehome.takehome_stack import TakehomeStack

# example tests. To run these tests, uncomment this file along with the example
# resource in takehome/takehome_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = TakehomeStack(app, "takehome")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
