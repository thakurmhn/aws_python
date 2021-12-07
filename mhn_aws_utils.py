import boto3

class AWSClients():

    def __init__(self, profile='', region='us-east-1'):

        self.profile = profile
        self.region = region
        self.aws_conn = boto3.session.Session(profile_name=self.profile, region_name=self.region)

    @staticmethod
    def get_account_id():
        aws_conn = AWSClients()
        sts_client = aws_conn.get_sts_client()
        response = sts_client.get_caller_identity()

        print(f"Account_ID: {response['Account']}")
        print(f"User_ARN: {response['Arn']}")

    def get_ec2_res(self):
        self.ec2_res = self.aws_conn.resource('ec2')
        return self.ec2_res

    def get_ec2_client(self):
        self.ec2_client = self.aws_conn.client('ec2')
        return self.ec2_client

    def get_iam_res(self):
        self.iam_res = self.aws_conn.resource('iam')
        return self.iam_res

    def get_iam_client(self):
        self.iam_client = self.aws_conn.client('iam')
        return self.iam_client

    def get_s3_res(self):
        self.s3_res = self.aws_conn.resource('s3')
        return self.s3_res

    def get_s3_client(self):
        self.s3_client = self.aws_conn.client('s3')
        return self.s3_client

    def get_sts_client(self):
        self.sts_client = self.aws_conn.client('sts')
        return self.sts_client

