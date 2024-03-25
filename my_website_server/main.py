from constructs import Construct
from cdktf import App, TerraformStack
from imports.aws import AwsProvider, S3Bucket, S3BucketObject, Instance, DataAwsIamPolicyDocument, IamRole, IamRolePolicyAttachment
import os

class MyEc2WebsiteStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        # AWS Provider
        AwsProvider(self, "AWS", region="us-east-1")

        # S3 Bucket for website content
        bucket = S3Bucket(self, "WebsiteBucket",
                          bucket="bucket_site_adam_moua",
                          acl="public-read")

        # Upload website content to S3 Bucket
        for root, _, files in os.walk("static-website.zip"):
            for file in files:
                file_path = os.path.join(root, file)
                S3BucketObject(self, f"S3Object{file.replace('.', '-')}",
                               bucket=bucket.bucket,
                               key=file_path.replace("\\", "/"),
                               source=file_path,
                               acl="public-read")

        # User Data to install web server and download content from S3
        user_data = """
        #!/bin/bash
        sudo apt update
        sudo apt install -y apache2
        sudo systemctl start apache2
        sudo systemctl enable apache2
        aws s3 cp s3://bucket_site_adam_moua /var/www/html/ --recursive
        """

        # EC2 Instance
        Instance(self, "WebServerInstance",
                 ami="ami-0c02fb55956c7d316",  
                 instance_type="t2.micro",
                 user_data=user_data,
                 tags={"Name": "MyWebServer"}
                 )

app = App()
MyEc2WebsiteStack(app, "my-ec2-website")
app.synth()
