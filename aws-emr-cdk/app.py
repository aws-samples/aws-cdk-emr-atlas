#!/usr/bin/env python3
import os

from aws_cdk import core
import yaml

from aws_emr_cdk.aws_emr_cdk_stack import AwsEmrCdkStack

f = open('./app-config.yml', 'r')
conf_map = yaml.safe_load(f)['emr']
f.close()

env_CN = core.Environment(account=conf_map['account'], region=conf_map['region'])

app = core.App()
AwsEmrCdkStack(app,
               conf_map['construct_id'],
               conf_map
    )

app.synth()
