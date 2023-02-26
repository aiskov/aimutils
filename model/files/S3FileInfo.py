import yaml
from typing import Dict, List, Any


class FileInfoVersion:
    def __init__(self, version_id: str, last_modified: str, is_delete_marker: bool):
        self.version_id = version_id
        self.last_modified = last_modified
        self.is_delete_marker = is_delete_marker


class FileInfo:
    def __init__(self, key: str, versions: List[FileInfoVersion] = None):
        self.key = key
        self.versions = versions if versions else []

    def add_version(self, version: FileInfoVersion):
        self.versions.append(version)

    @staticmethod
    def from_dump(fileRows: List[Dict[str, Any]]) -> List['FileInfo']:
        return [
            FileInfo(
                file['key'],
                [
                    FileInfoVersion(
                        version['version_id'],
                        version['last_modified'],
                        version['is_delete_marker']
                    )
                    for version in file['versions']
                ]
            )
            for file in fileRows
        ]

    def __str__(self):
        return yaml.dump([{
            'key': self.key,
            'versions': [
                {
                    'version_id': version.version_id,
                    'last_modified': version.last_modified,
                    'is_delete_marker': version.is_delete_marker
                }
                for version in self.versions
            ]
        }])
