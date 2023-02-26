from typing import List


class RevisionOfFileStoreReportFileVersionDto:
    def __init__(self, version_id: str, last_modified: str, is_delete_marker: bool):
        self.version_id = version_id
        self.last_modified = last_modified
        self.is_delete_marker = is_delete_marker


class RevisionOfFileStoreReportFileDto:
    def __init__(self, name: str, versions: List[RevisionOfFileStoreReportFileVersionDto] = None):
        self.name = name
        self.versions = versions if versions else []


class RevisionOfFileStoreReportDto:
    def __init__(self, files: List[RevisionOfFileStoreReportFileDto] = None):
        self.files = files if files else []
