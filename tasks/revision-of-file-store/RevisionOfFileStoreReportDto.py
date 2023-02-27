from typing import List
import yaml


class RevisionOfFileStoreReportFileVersionDto:
    def __init__(self, version_id: str, last_modified: str, is_delete_marker: bool):
        self.version_id = version_id
        self.last_modified = last_modified
        self.is_delete_marker = is_delete_marker


class RevisionOfFileStoreReportFileDto:
    def __init__(self, name: str, versions: List[RevisionOfFileStoreReportFileVersionDto] = None):
        self.name = name
        self.archived_date = []
        self.versions = versions if versions else []
        self.hints = []
        self.product_set_ids = []

    def add_version(self, version: RevisionOfFileStoreReportFileVersionDto):
        self.versions.append(version)

    def add_archived_date(self, archived_date: str):
        self.archived_date.append(archived_date)

    def add_hint(self, param):
        self.hints.append(param)

    def add_product_set_ids(self, set_ids):
        for set_id in set_ids:
            self.product_set_ids.append(set_id)


class RevisionOfFileStoreReportDto:
    def __init__(self, files: List[RevisionOfFileStoreReportFileDto] = None, not_found: List[str] = None):
        self.files = files if files else []
        self.not_found = set(not_found if not_found else [])

    def get(self, name: str) -> RevisionOfFileStoreReportFileDto:
        for file in self.files:
            if file.name == name:
                return file

        new = RevisionOfFileStoreReportFileDto(name)
        self.files.append(new)

        return new

    def add_not_found(self, name: str):
        self.not_found.add(name)

    def __str__(self):
        return yaml.dump({
            'bad_version': [
                {
                    'name': file.name,
                    'archived_date': file.archived_date,
                    'hints': file.hints,
                    'product_set_ids': file.product_set_ids,
                    'versions': [
                        {
                            'version_id': version.version_id,
                            'last_modified': version.last_modified,
                            'is_delete_marker': version.is_delete_marker
                        }
                        for version in file.versions
                    ]
                }
                for file in self.files
            ],
            'not_found': list(self.not_found)
        })
