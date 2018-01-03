import boto3
import argparse
import math
import re
import datetime

s3client = boto3.client('s3')
now = datetime.datetime.now()


def args():
    """
    This function is sued to add command line parameters
    """
    parser = argparse.ArgumentParser(
        description="This is a command-line utility \
        that returns information about S3 buckets in an Amazon AWS account.")

    parser.add_argument(
        "-u",
        "--unit",
        action="store",
        dest="unit",
        default="B",
        help="Specify your desired bucket size units (B, KB, MB, GB, TB)")

    parser.add_argument(
        "-b",
        "--bucket",
        action="store",
        dest="bucket",
        default="all",
        help="Filter buckets by partial name or regex \
            (e.g. buck or ^buck; no quotes)")

    parser.add_argument(
        "-s",
        "--sort",
        action="store",
        dest="sort",
        default=None,
        help="Specify column to sort by \
            (bucket, size, objects, created, modified, storage, region)")

    return parser.parse_args()


def convert_size(size_bytes, unit):
    if size_bytes is None:
        return 'N/A'
    if unit == 'B' or None:
        return '{:,}'.format(int(size_bytes))
    elif unit == 'KB':
        return '{:,.2f}'.format(size_bytes / math.pow(1024, 1))
    elif unit == 'MB':
        return '{:,.2f}'.format(size_bytes / math.pow(1024, 2))
    elif unit == 'GB':
        return '{:,.2f}'.format(size_bytes / math.pow(1024, 3))
    elif unit == 'TB':
        return '{:,.2f}'.format(size_bytes / math.pow(1024, 4))


def get_buckets(options):
    buckets = []
    # Get a list of all buckets
    all_buckets = s3client.list_buckets()['Buckets']
    if options == "all":
        for bucket in all_buckets:
            buckets.append(add_object_info(bucket))
    else:
        for bucket in all_buckets:
            if re.match(r'{}'.format(options), bucket['Name']) or options in bucket['Name']:
                buckets.append(add_object_info(bucket))
    return buckets


def add_object_info(bucket):
    last_modified = None
    storage_class = None
    s3object = s3client.list_objects_v2(Bucket=bucket["Name"])
    region = s3object['ResponseMetadata']['HTTPHeaders']['x-amz-bucket-region']

    if s3object['KeyCount'] != 0:
        last_modified = get_last_modified(s3object['Contents'])
        storage_class = s3object['Contents'][0]['StorageClass']

    bucket['Region'] = region
    bucket['LastModified'] = last_modified
    bucket['StorageClass'] = storage_class
    return bucket


def get_last_modified(content):
    content.sort(key=lambda k: k['LastModified'], reverse=True)
    date = content[0]['LastModified']
    return date.strftime("%Y-%m-%d %H:%M:%S")


def get_bucket_size(cloudwatch, bucket):
    # For each bucket item, look up the corresponding metrics from CloudWatch
    size = None
    bucket_size = cloudwatch.get_metric_statistics(
        Namespace='AWS/S3',
        MetricName='BucketSizeBytes',
        Dimensions=[
            {'Name': 'BucketName', 'Value': bucket['Name']},
            {'Name': 'StorageType', 'Value': 'StandardStorage'}
        ],
        Statistics=['Average'],
        Period=3600,
        StartTime=(now - datetime.timedelta(days=1)).isoformat(),
        EndTime=now.isoformat()
    )

    if len(bucket_size["Datapoints"]) != 0:
        size = bucket_size["Datapoints"][0]['Average']
    return size


def get_object_count(cloudwatch, bucket):
    count = None
    bucket_object_count = cloudwatch.get_metric_statistics(
        Namespace='AWS/S3',
        MetricName='NumberOfObjects',
        Dimensions=[
            {'Name': 'BucketName', 'Value': bucket['Name']},
            {'Name': 'StorageType', 'Value': 'AllStorageTypes'}
        ],
        Statistics=['Average'],
        Period=3600,

        StartTime=(now - datetime.timedelta(days=1)).isoformat(),
        EndTime=now.isoformat()
    )

    if len(bucket_object_count["Datapoints"]) != 0:
        count = bucket_object_count["Datapoints"][0]['Average']
    return count


def format_count(count):
    return str("{:,}".format(int(count)))
