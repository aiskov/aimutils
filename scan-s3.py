import argparse
from argparse import Namespace
from datetime import timezone
import boto3
from typing import List

from model.files.S3FileInfo import FileInfo
from model.files.S3FileInfo import FileInfoVersion


def list_files(bucket_name: str, prefix: str) -> List[FileInfo]:
    s3 = boto3.client('s3')

    files = {}

    # Set up initial request parameters
    request_params = {
        'Bucket': bucket_name,
        'Prefix': prefix,
        'MaxKeys': 100,
    }

    while True:
        # Make a request to list object versions
        response = s3.list_object_versions(**request_params)

        # Process each object version in the response
        for obj in response.get('Versions', []) + response.get('DeleteMarkers', []):
            key = obj['Key']

            if key not in files:
                files[key] = FileInfo(key)

            version = FileInfoVersion(
                obj['VersionId'],
                obj['LastModified'].replace(tzinfo=timezone.utc).isoformat(),
                obj.get('IsDeleteMarker', False)
            )

            files[key].add_version(version)

        # Check if there are more results
        if not response.get('IsTruncated', False):
            break

        # Set the request parameters for the next page of results
        request_params['KeyMarker'] = response['NextKeyMarker']
        request_params['VersionIdMarker'] = response['NextVersionIdMarker']

    return list(files.values())


def _print_files(files: List[FileInfo]):
    for file in files:
        print(file)


def _parse_args() -> Namespace:
    parser = argparse.ArgumentParser(description='List S3 bucket files and their versions.')

    parser.add_argument('bucket_name', type=str, help='Name of S3 bucket')
    parser.add_argument('prefix', type=str, help='Prefix of S3 objects to list')

    return parser.parse_args()


if __name__ == '__main__':
    args = _parse_args()

    result = list_files(args.bucket_name, args.prefix)
    _print_files(result)
