#!/usr/bin/env python3
# coding: utf-8

import argparse
import boto3
from jinja2 import Template
from botocore.exceptions import ClientError

def render_policy_doc(source_account, layer_arn):
    json_document = '''{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lambda:*"
            ],
            "Resource": "{{ arn }}",
            "Condition": {
                "StringEquals": {
                    "AWS:SourceAccount": "{{ account }}"
                }
            }
        }
    ]
}'''
    
    t = Template(json_document)
    json_rendered = t.render(arn=layer_arn, account=source_account)
    return json_rendered

def current_user():
    iam = boto3.resource('iam')
    current_user = iam.CurrentUser()
    
    return current_user

def create_policy(json_rendered): 
    iam_client = boto3.client('iam')
    
    try:
        response = iam_client.create_policy(
            PolicyName="AccessToLambda2",
            PolicyDocument=json_rendered,
            Description="Allows access to lambda layer"
        )
        return response
    except ClientError as error:
        print(error)
def attach_policy(user_name, policy):        
    # Policy Resources
    iam_client = boto3.client('iam')
    iam_client.attach_user_policy(UserName=user_name, PolicyArn=policy)

def main():
    parser = argparse.ArgumentParser(description='Parse aws account strings')
    parser.add_argument('--aws_account_id', type=str, required=True, help='The AWS account ID number of the account that owns or contains the calling entity.')
    parser.add_argument('--aws_region', type=str, required=True, help='The names of the region')
    parser.add_argument('--aws_profile', type=str, required=True, help='The names of the aws cli profile to use')
    args = parser.parse_args()

    aws_account = args.aws_account_id
    region = args.aws_region
    profile = args.aws_profile

    user = current_user()
    user_id = user.user_id
    user_name = user.user_name
    
    json_rendered = render_policy_doc(aws_account, "arn:aws:lambda:us-east-1:193632271191:layer:pwnlib38")

    policy = create_policy(json_rendered)
    print("policy: " + str(policy) + str(type(policy)))
    policy_arn = policy['Policy']['Arn']
    attach_policy(user_name, policy_arn)

    


if __name__ == '__main__':
    main()