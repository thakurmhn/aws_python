#!/usr/bin/env python3.7

import argparse
from mhn_aws_utils import AWSClients
import sys

#######################################################################################
#       CHANGE ME
#       Default Variables used to create instances
#       Replace the values if you want to set your own default values
#       you can override default values with create option; see ./prog_name create -h
#######################################################################################
AWS_PROFILE = 'default'                     # AWS Profile Name
AMI_ID = 'ami-02e136e904f3da870'            # AmiId
INSTANCE_TYPE = 't2.micro'                  # InstanceType t2.micro, t3.medium etc
SUBNET_ID = 'subnet-0b03fae5e80a9b776'      # SubnetId
TAG_NAME = 'TEST_INSTANCE'                  # NameTag
SG_ID = 'sg-0ed50b83ded8e2589'              # SecurityGroupId
KEYPAIR_NAME = 'home_new_hostmail'          # SSH-KeyPairName
InstanceProfile = ''                        #'Iam_Role_with_S3_full_Access'

######################################################################################

parser = argparse.ArgumentParser(description="Script to manage EC2 Instances")
subparser = parser.add_subparsers(dest='command')
create = subparser.add_parser('create', help="Launch an EC2 instance default arguments; use -h to see override options")
create.add_argument('--profile', nargs='?', help="Provide AWS Profile Name; default is 'default'", default=AWS_PROFILE)
create.add_argument('-I', nargs='?', default=AMI_ID, help='Provide AmiId; if not provided defualt is used')
create.add_argument('-i', nargs='?', default=INSTANCE_TYPE, help='Provide InstanceType; defualt is t2.micro')
create.add_argument('-s', nargs='?', default=SUBNET_ID, help='Provide subnet if need to spin up instance in other that default subnet')
create.add_argument('-t', nargs='?', default=TAG_NAME, help='Provide Name Tag for the Instance')
create.add_argument('-c', nargs='?', type=int, default=1, help='Provide Count, Number of instances to be spined up')
create.add_argument('-g', nargs='?', default=SG_ID, help='Provide Security group ID')
create.add_argument('-k', nargs='?', default=KEYPAIR_NAME, help='Provide SSH KEY Pair Name')
create.add_argument('-p', nargs='?', default=InstanceProfile, help="Provide Instance Profile Role Name")

parser.add_argument("--profile", help="Provide your aws credential profile if not default", default=AWS_PROFILE)
parser.add_argument("--list", help="list running ec2 instances with given Tag", metavar="<Instance Name Tag>")
parser.add_argument("--account", help="Get Account information", action="store_true")
parser.add_argument("--stop", help="Stops instance with provided instance_id", metavar="<instance_id>")
parser.add_argument("--start", help="Starts instance with provided instance_id", metavar="<instance_id>")
parser.add_argument("--terminate", help="Terminate instance with provided instance_id", metavar="<instance_id>")
parser.add_argument("--status", help="Shows instance status", metavar="<instance_id>")

args = parser.parse_args()

def show_public_ip(instance_id):
    aws_conn = AWSClients(profile=args.profile)
    ec2_res = aws_conn.get_ec2_res()
    response = ec2_res.Instance(instance_id)
    public_ip = response.public_ip_address
    return public_ip

def get_account_info():
    AWSClients.get_account_id()

def list_instances_by_tag():
    aws_conn = AWSClients(profile=args.profile)
    ec2_res = aws_conn.get_ec2_res()
    instance_iterator = ec2_res.instances.filter(
        Filters=[
            {
            'Name': 'tag:Name',
            'Values': [args.list]
        }
    ]
    )
    for instance in instance_iterator:
        response = ec2_res.Instance(instance.id)
        print(f"{instance.id}\t {response.state['Name']}\t {response.tags[0]['Value']}")

def launch_instance():
    LOG.info(f"Using AMI_ID {args.I}")
    aws_conn = AWSClients(profile=args.profile)
    ec2_client = aws_conn.get_ec2_client()
    response = ec2_client.run_instances(
        BlockDeviceMappings=[
            {
                'DeviceName': '/dev/xvda',
                'Ebs': {

                    'DeleteOnTermination': True,
                    'VolumeSize': 30,
                    'VolumeType': 'gp2'
                },
            },
        ],
        ImageId=args.I,
        InstanceType=args.i,
        SubnetId=args.s,
        SecurityGroupIds=[args.g],
        KeyName=args.k,
        IamInstanceProfile={
                    'Name': args.p
        },
        TagSpecifications=[
                          {
                              'ResourceType': 'instance',
                              'Tags': [
                                  {
                                      'Key': 'Name',
                                      'Value': args.t
                                  },
                              ]
                          },
                      ],
        MaxCount=args.c,
        MinCount=args.c

    )

    print("Please wait while Instance is being Launched......")
    waiter = ec2_client.get_waiter('instance_running')
    waiter.wait(InstanceIds=[response['Instances'][0]['InstanceId']])

    print(f"\nLaunched Instane with Following Details\n")
    print(f"Instance_ID: {response['Instances'][0]['InstanceId']}")
    print(f"SSH-KeyParName: {response['Instances'][0]['KeyName']}")
    print(f"PrivateIP: {response['Instances'][0]['PrivateIpAddress']}")
    public_ip = show_public_ip(response['Instances'][0]['InstanceId'])
    print(f"PublicIP: {public_ip}")
    print(f"Name-Tag: {args.t}")

def stop_instance(instance_id):
    aws_con = AWSClients(profile=args.profile)
    ec2_client = aws_con.get_ec2_client()
    ec2_client.stop_instances(InstanceIds=[instance_id])
    waiter = ec2_client.get_waiter('instance_stopped')
    print(f"Waiting to stop Instance............. {instance_id}")
    waiter.wait(InstanceIds=[instance_id])

def start_instance(instance_id):
    aws_con = AWSClients(profile=args.profile)
    ec2_client = aws_con.get_ec2_client()
    ec2_client.start_instances(InstanceIds=[instance_id])
    waiter = ec2_client.get_waiter('instance_running')
    print(f"Waiting  to start Instance............. {instance_id}")
    waiter.wait(InstanceIds=[instance_id])

def terminate_instance(instance_id):
    aws_con = AWSClients(profile=args.profile)
    ec2_client = aws_con.get_ec2_client()
    ec2_client.terminate_instances(InstanceIds=[instance_id])
    waiter = ec2_client.get_waiter('instance_terminated')
    print(f"Waiting to Terminate the instance.............{instance_id}")
    waiter.wait(InstanceIds=[instance_id])

def instance_status(instance_id):
    aws_con = AWSClients(profile=args.profile)
    ec2_resource = aws_con.get_ec2_res()
    response = ec2_resource.Instance(instance_id)
    return response.state['Name']

def main():
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
    if args.list:
        list_instances_by_tag()
    if args.account:
        get_account_info()
    if args.command == 'create':
        launch_instance()
    if args.stop:
        instance_id = args.stop
        stop_instance(instance_id)
    if args.start:
        instance_id = args.start
        start_instance(instance_id)
    if args.terminate:
        instance_id = args.terminate
        terminate_instance(instance_id)
    if args.status:
        instance_id = args.status
        print(f"{instance_id} is in {instance_status(instance_id)} State")

if __name__ == '__main__':
    main()
















