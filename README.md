# aws-emr-cdk-atlas

A CDK stack to deploy Amazon EMR with Atlas.

# What does the code do?
1. Creates an AWS EMR cluster within a new VPC.
2. Creates an IAM service role for the EMR cluster to read scripts from s3 bucket.


# How to use the code?
## Install AWS CDK
Please refer to the following the [link](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html)

## AWS cli config 
Please refer to the following the [link](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)

## Install git

## Initialize the CDK directory
    
    git clone https://github.com/aws-samples/aws-cdk-emr-atlas
    cd aws-cdk-emr-atlas/aws-emr-cdk/

## Activate the virtualenv and install dependencies
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    pip3 install PyYAML
    pip3 install aws_cdk.core
    pip3 install aws_cdk.aws_emr
    pip3 install aws_cdk.aws_ec2


## Change the configurations
Update the configurations in the app-config.yml file.

Before deploy, here is something you need to know:

1. You need a key pair config to EC2, which config in app-config.yaml file as emr->ec2->key_pair.
2. You need to create two S3 bucket, and config it in app-config.yaml for s3_log_bucket and s3_script_bucket.
3. Put file  aws-cdk-emr-atlas/aws-emr-cdk/apache-atlas-emr.sh to the bucket, which is the value of 's3_script_bucket' key in app-config.yaml.
4. The IAM role and job flow role for EMR service, will be created automatically.
5. A VPC with public subnet will be created automatically.

## Now let's deploy!
    cdk synth  # To review the cloudformation template
    cdk diff  # To review the change set
    cdk deploy  # To deploy the stack

## Test EMR
After you deploy the stack, you could find a EMR cluster in the console, try to connect the master node in terminal 
to run a job, and test other services on it, or add a step on the console to test Hadoop and Spark.

## Run a job on EMR cluster
# Additional Resources:
1. AWS Best Practice: [link](https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-plan-instances-guidelines.html)
2. Resizing a cluster: [link](https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-manage-resize.html)
3. Submit a job on console: [link](https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-add-steps-console.html)
4. Submit Hadoop jobs interactively: [link](https://docs.aws.amazon.com/emr/latest/ManagementGuide/interactive-jobs.html)
5. You can terminate a EMR cluster by console/CLI/APIA: [link](https://docs.aws.amazon.com/emr/latest/ManagementGuide/UsingEMR_TerminateJobFlow.html)
