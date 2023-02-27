from collections import defaultdict

import csv
import os
import sys
import yaml
from typing import Dict, List, Optional

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)


from model.files.S3FileInfo import FileInfo
from RevisionOfFileStoreReportDto import RevisionOfFileStoreReportDto, RevisionOfFileStoreReportFileVersionDto
from DbExportDto import DbExportDto


def load_db_export_file(filename: str) -> List['DbExportDto']:
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return DbExportDto.from_csv(reader)


def load_s3_export_file(filename: str) -> Dict[str, 'FileInfo']:
    with open(filename, 'r') as f:
        return {
            record.key: record
            for record in FileInfo.from_dump(yaml.safe_load(f))
        }


def find_file_info(s3_files: List[FileInfo], key: str) -> Optional[FileInfo]:
    for file_info in s3_files:
        if file_info.key == key:
            return file_info

    return None


def find_files_with_archive_date_after_last_modified(db_data: List[DbExportDto], s3_data: Dict[str, FileInfo]) \
        -> RevisionOfFileStoreReportDto:

    report = RevisionOfFileStoreReportDto()

    grouped = defaultdict(list)
    for row in db_data:
        grouped[f'product-attachments/{row.product_id}/{row.name}'].append(row)

    for file_name, rows in grouped.items():
        s3_file = s3_data.get(file_name, None)

        if not s3_file:
            report.add_not_found(file_name)
            continue

        _process_db_row(report, rows, s3_file)

    return report


def _process_db_row(report: RevisionOfFileStoreReportDto, rows: List[DbExportDto], s3_file: FileInfo):
    # Check if there is file which have no versions
    if len(s3_file.versions) == 1 and s3_file.versions[0].version_id == 'null':
        _report_problems("FIRST_NULL_VERSION: Re upload version and save new version in db.",
                         report, rows, s3_file, [row.product_set_id for row in rows])

    # Check if there is wrong assignment
    for row in rows:
        if not row.archive_date:
            continue

        s3_version = s3_file.find_version(row.storage_version_id)

        if not s3_version:
            _report_problems(f"Wrong assignment, version with id {row.storage_version_id or 'null'} doesn't exists. "
                             + "Should be manually solved.", report, rows, s3_file)

            continue

        if s3_version.last_modified > row.archive_date:
            _report_problems("Wrong assignment, version is newer than archive date."
                             + "Should be manually solved", report, rows, s3_file)

        if not row.storage_version_id:
            _report_problems("OVERWRITTEN_NULL: Version should be peeked to top. ",
                             report, rows, s3_file, [row.product_set_id])


def _report_problems(hint: str, report: RevisionOfFileStoreReportDto, rows: List[DbExportDto],
                     s3_file: FileInfo, set_ids: List[str] = None):

    report_record = report.get(s3_file.key)

    for row in rows:
        report_record.add_archived_date(row.archive_date)

    report_record.add_version(
        RevisionOfFileStoreReportFileVersionDto(
            s3_file.versions[0].version_id,
            s3_file.versions[0].last_modified,
            s3_file.versions[0].is_delete_marker
        )
    )
    report_record.add_hint(hint)

    if set_ids:
        report_record.add_product_set_ids(set_ids)


if __name__ == '__main__':
    s3_file_infos = load_s3_export_file('s3_export.yaml')
    db_rows = load_db_export_file('db_export.csv')

    results = find_files_with_archive_date_after_last_modified(db_rows, s3_file_infos)

    print(results)
