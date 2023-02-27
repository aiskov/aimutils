import argparse
import yaml
import boto3


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Regenerate bad versions.')
    parser.add_argument('bucket', type=str, help='Name of S3 bucket')

    return parser.parse_args()


def recreate(bucket, file_key) -> str:
    s3 = boto3.client('s3')

    response = s3.copy_object(
        Bucket=bucket,
        CopySource={
            'Bucket': bucket,
            'Key': file_key,
            'VersionId': 'null'
        },
        Key=file_key
    )

    return response['VersionId']


if __name__ == '__main__':
    args = _parse_args()

    with open('analysis-result.yaml', 'r') as f:
        data = yaml.safe_load(f)

    bad_versions = [
        version
        for version in data.get('bad_version', [])
        if any(hint.startswith('FIRST_NULL_VERSION')
               for hint in version.get('hints', []))
    ]

    for version in bad_versions:
        key = version['name']
        name = key[key.rindex('/') + 1:]

        new_storage_version_id = recreate(args.bucket, key)

        print(
            f"UPDATE product_file SET storage_version_id = '{new_storage_version_id}' "
            f"WHERE name = '{name}' AND product_file_set_id IN ({', '.join(version['product_set_ids'])});"
        )
