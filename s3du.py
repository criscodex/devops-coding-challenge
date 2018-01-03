from table_logger import TableLogger
from helpers import *

args = args()

class S3du(object):

    def get_bucket_stats(self):
        # Get the list of buckets
        buckets = get_buckets(args.bucket)
        list_buckets = []
        if args.sort is None:
            buckets.sort(key=lambda k: k['Region'])

        # Iterate through each bucket
        for bucket in buckets:
            cloudwatch = boto3.client('cloudwatch', region_name=bucket['Region'])

            size = get_bucket_size(cloudwatch, bucket)
            count = get_object_count(cloudwatch, bucket)

            if args.sort is None:
                table(bucket['Name'],
                      bucket['CreationDate'].strftime("%Y-%m-%d %H:%M:%S"),
                      bucket['LastModified'] if bucket['LastModified'] else 'N/A',
                      convert_size(size, args.unit) if size else 'N/A',
                      format_count(count) if count else 'N/A',
                      bucket['StorageClass'] if bucket['StorageClass'] else 'N/A',
                      bucket['Region'])
            else:
                collection = {"bucket": bucket["Name"],
                              "created": bucket["CreationDate"].strftime("%Y-%m-%d %H:%M:%S"),
                              "size": size if size else 0,
                              "objects": int(count) if count else 0,
                              "modified": bucket['LastModified'],
                              "storage": bucket['StorageClass'],
                              "region": bucket["Region"]}

                list_buckets.append(collection)

        list_buckets.sort(key=lambda k: k[args.sort], reverse=True)

        return list_buckets


if __name__ == '__main__':
    # Table header
    table = TableLogger(columns='Bucket Name,Date Created (UTC),Last Modified (UTC),Size ({})'
                                ',Objects,Storage Class,Region'
                        .format(args.unit),
                        colwidth={'Bucket Name': 40,
                                'Date Created(UTC)': 25,
                                'Last Modified(UTC)': 25,
                                'Size (bytes)': 20,
                                'Objects': 10,
                                'Storage Class': 20,
                                'Region': 20})
    s3du = S3du()
    bucket_stats = s3du.get_bucket_stats()
    if args.sort:
        for stat in bucket_stats:
            table(stat['bucket'],
                  stat['created'],
                  stat['modified'] if stat['modified'] else 'N/A',
                  convert_size(stat['size'], args.unit) if stat['size'] != 0 else 'N/A',
                  format_count(stat['objects']) if stat['objects'] != 0 else 'N/A',
                  stat['storage'] if stat['storage'] else 'N/A',
                  stat['region'])
