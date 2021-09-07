from aws_cdk import aws_ec2 as ec2, aws_iam as iam, core, aws_emr as emr
# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core


class AwsEmrCdkStack(core.Stack):

    def __init__(self,
                 scope: core.Construct,
                 construct_id: str,
                 conf_map: dict,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC
        vpc = ec2.Vpc(
            self,
            "vpc",
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public", subnet_type=ec2.SubnetType.PUBLIC
                )
            ],
        )


        # enable reading scripts from s3 bucket
        read_scripts_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["s3:GetObject",],
            resources=[f"arn:aws-cn:s3:::{conf_map['emr_cluster']['s3_script_bucket']}/*"],
        )
        read_scripts_document = iam.PolicyDocument()
        read_scripts_document.add_statements(read_scripts_policy)

        # emr service role
        emr_service_role = iam.Role(
            self,
            "emr_service_role",
            assumed_by=iam.ServicePrincipal("elasticmapreduce.amazonaws.com"),
            role_name=conf_map['emr_cluster']['service_role_name'],
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonElasticMapReduceRole"
                )
            ],
            inline_policies=[read_scripts_document],
        )

        # emr job flow role
        emr_job_flow_role = iam.Role(
            self,
            "emr_job_flow_role",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonElasticMapReduceforEC2Role"
                )
            ],
        )
        # emr job flow profile
        emr_job_flow_profile = iam.CfnInstanceProfile(
            self,
            "emr_job_flow_profile",
            roles=[emr_job_flow_role.role_name],
            instance_profile_name=conf_map['emr_cluster']['instance_profile_name'],
        )

        # key pair
        # key_pair = ec2.KeyPair(key_name="", public_key="")

        # create emr cluster
        emr.CfnCluster(
            self,
            id="emr_cluster",
            instances=emr.CfnCluster.JobFlowInstancesConfigProperty(
                ec2_key_name=conf_map['ec2']['key_pair'],
                core_instance_group=emr.CfnCluster.InstanceGroupConfigProperty(
                    instance_count=2,
                    instance_type=conf_map['ec2']['slave_instance_type'],
                    market=conf_map['ec2']['market']  # Allowed values: ON_DEMAND | SPOT
                    # update instance type
                ),
                ec2_subnet_id=vpc.public_subnets[0].subnet_id,
                # hadoop_version="2.4.0",
                keep_job_flow_alive_when_no_steps=True,
                master_instance_group=emr.CfnCluster.InstanceGroupConfigProperty(
                    instance_count=1, instance_type=conf_map['ec2']['master_instance_type'], market=conf_map['ec2']['market']
                ),
            ),
            # note job_flow_role is an instance profile (not an iam role)
            job_flow_role=emr_job_flow_profile.instance_profile_name,
            name=conf_map['emr_cluster']['domain_name'],
            applications=[emr.CfnCluster.ApplicationProperty(name="Hadoop"),
                          emr.CfnCluster.ApplicationProperty(name="Hive"),
                          emr.CfnCluster.ApplicationProperty(name="HBase"),
                          emr.CfnCluster.ApplicationProperty(name="Presto"),
                          emr.CfnCluster.ApplicationProperty(name="Hue"),
                          emr.CfnCluster.ApplicationProperty(name="ZooKeeper"),
                          emr.CfnCluster.ApplicationProperty(name="Spark")   # ,emr.CfnCluster.ApplicationProperty(name="Sqoop")
                          ],
            service_role=emr_service_role.role_name,
            configurations=[
                # use python3 for pyspark
                emr.CfnCluster.ConfigurationProperty(
                    classification="spark-env",
                    configurations=[
                        emr.CfnCluster.ConfigurationProperty(
                            classification="export",
                            configuration_properties={
                                "PYSPARK_PYTHON": "/usr/bin/python3",
                                "PYSPARK_DRIVER_PYTHON": "/usr/bin/python3",
                            },
                        )
                    ],
                ),
                # enable apache arrow
                emr.CfnCluster.ConfigurationProperty(
                    classification="spark-defaults",
                    configuration_properties={
                        "spark.sql.execution.arrow.enabled": "true"
                    },
                ),
                # dedicate cluster to single jobs
                emr.CfnCluster.ConfigurationProperty(
                    classification="spark",
                    configuration_properties={"maximizeResourceAllocation": "true"},
                ),
            ],
            log_uri=f"s3://{conf_map['emr_cluster']['s3_log_bucket']}/{core.Aws.REGION}/elasticmapreduce/",
            release_label=conf_map['emr_cluster']['relase_label'],
            visible_to_all_users=True, # False to True 6.25 3:40
            ebs_root_volume_size=50,
            # the job to be done
            steps=[
                emr.CfnCluster.StepConfigProperty(
                    hadoop_jar_step=emr.CfnCluster.HadoopJarStepConfigProperty(
                        jar="s3://cn-northwest-1.elasticmapreduce/libs/script-runner/script-runner.jar",
                        args=[f"s3://{conf_map['emr_cluster']['step_file_bucket_name']}/{conf_map['emr_cluster']['step_script_file_name']}"
                        ],
                    ),
                    name="setup_atlas",
                    action_on_failure="CONTINUE"
                ),
            ],
        )
