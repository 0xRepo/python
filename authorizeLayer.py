#!/usr/bin/env python3
# coding: utf-8

import argparse
import boto3
import logging
import os
import sys
import re
from jinja2 import Template
from botocore.exceptions import ClientError


# You can use cross-account roles to give accounts that you trust access to Lambda actions and resources. If you just want to grant permission to invoke a function or use a layer, use resource-based policies instead.
# Doc here: https://docs.aws.amazon.com/lambda/latest/dg/access-control-resource-based.html
# Doc for Cross-Account Role: https://docs.aws.amazon.com/lambda/latest/dg/access-control-identity-based.html
# Granting Layer Access to Other Accounts: https://docs.aws.amazon.com/lambda/latest/dg/access-control-resource-based.html#permissions-resource-xaccountlayer
aws_profile = os.environ['AWS_PROFILE']
runtimes = ['python3.6', 'python3.7', 'python3.8']


def render_policy_doc(source_account, arn1, arn2, arn3):
    json_document = '''{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lambda:*"
            ],
            "Resource": [
                "{{ runtime1 }}",
                "{{ runtime2 }}",
                "{{ runtime3 }}"
            ],
            "Condition": {
                "StringEquals": {
                    "AWS:SourceAccount": "{{ account }}"
                }
            }
        }
    ]
}'''

    t = Template(json_document)
    # There are 3 python runtimes
    json_rendered = t.render(runtime1=arn1,
                             runtime2=arn2,
                             runtime3=arn3,
                             account=source_account)
    return json_rendered


def current_user():
    iam = boto3.resource('iam')
    current_user = iam.CurrentUser()

    return current_user


def create_policy(json_rendered, user):
    iam_client = boto3.client('iam')

    try:
        response = iam_client.create_policy(
            PolicyName="{}-AccessToLambda2".format(user),
            PolicyDocument=json_rendered,
            Description="Allows access to lambda layer"
        )
        return response
    except ClientError as error:
        print(error)
        sys.exit()


def attach_policy(user_name, policy):
    # Policy Resources
    iam_client = boto3.client('iam')
    iam_client.attach_user_policy(UserName=user_name, PolicyArn=policy)


def list_layer_versions():
    client = boto3.client('lambda')
    layer_versions = {}
    i = 0
    for runtime in runtimes:
        layers = client.list_layers(
            CompatibleRuntime=runtime
        )
        for layer in layers['Layers']:
            versions = client.list_layer_versions(LayerName=layer['LayerName'])
            layer_versions.update({runtime: versions})

    return layer_versions


def latestLayers():
    client = boto3.client('lambda')
    response = client.list_layers()

    total = len(response['Layers'])
    layers = {}
    for i in list(range(total)):
        layers[i] = response['Layers'][i]

    versions = client.list_layer_versions

    latest = []

    for i in list(range(len(layers))):
        if re.findall(r'python', str(layers[i]['LatestMatchingVersion']['CompatibleRuntimes'])):
            latest.append(layers[i]['LatestMatchingVersion']
                          ['LayerVersionArn'])
    breakpoint()
    return latest


def main():
    parser = argparse.ArgumentParser(description='Parse aws account strings')
    parser.add_argument('--aws_account_id', type=str, required=True,
                        help='The AWS account ID number of the account that owns or contains the calling entity.')
    parser.add_argument('--aws_region', type=str,
                        required=True, help='The names of the region')
    parser.add_argument('--aws_profile', type=str, required=False, default=os.environ['AWS_PROFILE'],
                        help='The names of the aws cli profile to use')
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',
                        filename='logs/authorizeLambda.log', filemode='w', level=logging.DEBUG)
    logging.info('Started')

    aws_account = args.aws_account_id
    region = args.aws_region
    profile = args.aws_profile
    user = current_user()
    user_id = user.user_id
    user_name = user.user_name

    latest = latestLayers()

    json_rendered = render_policy_doc(
        aws_account, latest[0], latest[1], latest[2])

    policy = create_policy(json_rendered, user_name)
    policy_arn = policy['Policy']['Arn']
    attach_policy(user_name, policy_arn)

    logging.info('Finished')


if __name__ == '__main__':
    main()
