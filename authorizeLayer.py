"""
Code a tool in python, that takes the following as input:
	* a customer aws account id
	* an aws region, and 
	* an aws profile
	
	Goal: adds permission to access the lambda layers, for the customer aws account id. 
	
	Note that the profile is the profile the person running the script has, and is to ensure that the person running the tool has the right privileges to run the tool.
"""

"""
Successfully done:
- create a policy using client
- attach a policy using hardcoded PolicyArn
- accept user input

Not done:
- interraction between functions
- remove hardcoded values :(
"""

import boto3
from botocore.exceptions import ClientError
import argparse
import json

def parse_args():
    parser = argparse.ArgumentParser(description='Parse aws account strings')
    parser.add_argument('aws_account_id', type=str, required=True, help='The AWS account ID number of the account that owns or contains the calling entity.')
    parser.add_argument('aws_region', type=str, required=True, help='The names of the region')
    parser.add_argument('aws_profile', type=str, required=True, help='The names of the aws cli profile to use')
    args = parser.parse_args()

    aws_account = args.aws_account_id
    region = args.aws_region
    profile = args.aws_profile


def list_layers():
    client = boto3.client('lambda')
    versions = ["python3.6", "python3.7", "python3.8"]
    response = {}
    i = 0
    for version in versions:
        response[i] = client.list_layers(
                CompatibleRuntime=version

            )
        print(str(i) + ": " + str(response[i]))
        i+=1

layer_arn_test = "arn:aws:lambda:us-east-1:193632271191:layer:pwnlib36:1"
# Relies on the output of list layers for:
# - layers name / arn or other identifiers to add to the policy document
#var = "test"
#policy_json = '''\
#{\
#    "Version": "2012-10-17",\
#    "Statement": [{\
#        "Effect": "Allow",\
#        "Action": [\
#            "lambda:*"\
#        ],\
#        "Condition": {\ 
#            "AWS:SourceAccount": "{source_account}"\
#         }\
#        "Resource": "arn:aws:lambda:us-east-1:193632271191:layer:pwnlib38:1"\
#    }]\
#}\
#'''

print(policy_json())
def create_policy_document():
    # Idea from: https://medium.com/@manmohan.bohara/automating-aws-iam-using-lambda-and-boto3-part-1-404eb507e85b
    iam_client = boto3.client('iam')
    policy = { 'Version' : '2012-10-17'}
    arn = "test"
    policy['Statement'] = [{'Sid' : 'AwsIamUserPython', 
                        'Effect': 'Allow', 
                        'Action': 'lambda:*', 
                        'Resource': '{var}'}].format(arn)
    policy_json = json.dumps(policy, indent=2)

    try:
        iam_client.create_policy(
            PolicyName="AccessToLambda",
            PolicyDocument=policy_json,
            Description="Allows access to lambda layer"
        )
    except ClientError as error:
        print(error)

def attach_policy():        
    iam = boto3.resource('iam')
    # User resources
    current_user = iam.CurrentUser()
    user_id = current_user.user_id
    user_name = current_user.user_name
    user_arn = current_user.arn
    
    # Policy Resources
    policy = iam.UserPolicy(user_name, 'AccessToLambda')
    iam_client = boto3.client('iam')
    iam_client.attach_user_policy(UserName=user_name, PolicyArn='arn:aws:iam::193632271191:policy/AccessToLambda')

def main():

if __name__ == '__main__':
    parse_args()
    attach_policy()
    list_layers()
    