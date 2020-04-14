import boto3
import json
import pickle
import csv

ec2 = boto3.client('ec2')
vpc_file = "vpc_list.txt"
bucket_name = "diya-bucket"
region = "us-east-2"
vpc_rows= []

# def check_bucket_or_create(s3_client):
#     s3 = boto3.resource('s3')
#     exist = s3.Bucket('diya-test-bucket') in s3.buckets.all()
#     if exist:
#         print("Bucket Exist")
#     else:
#         print("Bucket does not exist")
#         s3_client.create_bucket(Bucket='diya-test-bucket')

def bucket_exists():
  s3 = boto3.resource('s3')
  return s3.Bucket(bucket_name) in s3.buckets.all()

def create_bucket():
    s3_client = boto3.client('s3', region_name=region)
    location = {'LocationConstraint': region}
    s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
    

def key_create(s3, vpc_rows):
    response = s3.put_object(
             Bucket=bucket_name,
             Key=vpc_file,
             Body=vpc_rows,
             
         )


def s3_upload(vpc_rows):
    s3 = boto3.client('s3')
    vpc_rows = str(vpc_rows)

    if bucket_exists():
      print("BUCKET EXISTS")
    else:
        print("BUCKET DOES NOT EXISTS")
        create_bucket()
        key_create(s3, vpc_rows)
        return

    

    s3r = boto3.resource('s3')
    obj = s3r.Object(bucket_name, vpc_file)
    body2 = obj.get()['Body'].read().decode(encoding="utf-8",errors="ignore")


    if body2 == vpc_rows:
        print("VPC REMAINS UNCHANGED")
    else:
        print("VPC CHANGED")
        print(body2[1])
        print(vpc_rows)
        key_create(s3, vpc_rows)
        


def lambda_handler(event, context):
    # TODO implement


    # Retrieves all regions/endpoints that work with EC2
    response = ec2.describe_regions()
    regions = response['Regions']
 

    for rgn in regions:
        region = rgn['RegionName']
        ec2_regions = boto3.client('ec2', region_name=region)
        
  

        response = ec2_regions.describe_vpcs()
        vpcs = response['Vpcs']
      

        for vpc in vpcs:
            CidrBlock = vpc['CidrBlock']
            VpcId = vpc['VpcId']
            vpc_row = {'region': region, 'CidrBlock': CidrBlock, 'VpcId': VpcId }
            vpc_rows.append(vpc_row)
            # print("     ::::::::::::::::::::::: VPC ROW ::::::::::: ", vpc_row)
            





    # write_file(vpc_rows)
    s3_upload(vpc_rows)

    return {
        # 'vpc_lists': vpc_rows,
        'statusCode': 200,
        'body': json.dumps('Execution successfull')
    }



