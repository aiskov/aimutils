import argparse
import boto3

from commons import crop_slash


def copy_all_versions(source_bucket, source_key, destination_bucket, destination_key):
    s3 = boto3.client('s3')

    source_key = crop_slash(source_key)
    destination_key = crop_slash(destination_key)

    print(f'Looking for file versions in {source_bucket}/{source_key}...')

    versions = s3.list_object_versions(Bucket=source_bucket, Prefix=source_key)
    print(f'Found {len(versions.get("Versions", []))} versions and '
          f'{len(versions.get("DeleteMarkers", []))} delete markers.')

    for version in versions.get('Versions', []):
        print(f'Copying {source_key} version {version["VersionId"]} to {destination_key}...')

        s3.copy_object(Bucket=destination_bucket,
                       CopySource={'Bucket': source_bucket, 'Key': source_key, 'VersionId': version['VersionId']},
                       Key=destination_key)

    for version in versions.get('DeleteMarkers', []):
        print(f'Copying {source_key} delete marker {version["VersionId"]} to {destination_key}...')

        s3.copy_object(Bucket=destination_bucket,
                       CopySource={'Bucket': source_bucket, 'Key': source_key, 'VersionId': version['VersionId']},
                       Key=destination_key)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Copy all versions of a file from one S3 bucket to another.')

    parser.add_argument('source_bucket', help='The name of the source S3 bucket')
    parser.add_argument('source_key', help='The key of the source file in the source S3 bucket')
    parser.add_argument('destination_bucket', help='The name of the destination S3 bucket')
    parser.add_argument('destination_key', help='The key of the destination file in the destination S3 bucket')

    return parser.parse_args()


if __name__ == '__main__':
    args = _parse_args()
    copy_all_versions(args.source_bucket, args.source_key, args.destination_bucket, args.destination_key)
