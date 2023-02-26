import csv
import os
import sys
import yaml
from typing import Dict, List, Optional, Any

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)


from model.files.S3FileInfo import FileInfo
from RevisionOfFileStoreReportDto import RevisionOfFileStoreReportFileDto, RevisionOfFileStoreReportDto, \
    RevisionOfFileStoreReportFileVersionDto
from DbExportDto import DbExportDto


def load_db_export_file(filename: str) -> List['DbExportDto']:
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return DbExportDto.from_csv(reader)


def load_s3_export_file(filename: str) -> List[Dict[str, Any]]:
    with open(filename, 'r') as f:
        return yaml.safe_load(f)


def find_file_info(s3_files: List[FileInfo], key: str) -> Optional[FileInfo]:
    for file_info in s3_files:
        if file_info.key == key:
            return file_info
    return None


def find_files_with_archive_date_after_last_modified(db_data: List[DbExportDto], s3_data: List[FileInfo]) \
        -> RevisionOfFileStoreReportDto:

    report = RevisionOfFileStoreReportDto()

    for row in db_data:
        _process_db_row(report, row, s3_data)

    return report


def _process_db_row(report, row: DbExportDto, s3_files):
    found = False

    for s3_file in s3_files:
        if row.name in s3_file.key and f'product-attachments/{row.product_id}/' in s3_file.key:
            for version in s3_file.versions:
                if version.last_modified and row.archive_date and row.archive_date < version.last_modified:
                    found = True

                    file_dto = RevisionOfFileStoreReportFileDto(
                        s3_file.key,
                        [RevisionOfFileStoreReportFileVersionDto(
                            version.version_id,
                            version.last_modified,
                            version.is_delete_marker
                        )]
                    )

                    report.files.append(file_dto)
                    break

            if found:
                break

    if not found:
        file_dto = RevisionOfFileStoreReportDto(row.name)
        report.files.append(file_dto)


if __name__ == '__main__':
    s3_file_infos = FileInfo.from_dump(
        load_s3_export_file('s3_export.yaml')
    )

    db_rows = load_db_export_file('db_export.csv')

    results = find_files_with_archive_date_after_last_modified(db_rows, s3_file_infos)

    print(results)


    # # Print the results
    # if not results:
    #     print('No files found that violate the rule')
    # else:
    #     print('Files with archive_date after last_modified:')
    #     for r in results:
    #         print(f"{r['key']} (product ID: {r['product_id']}) - archive_date: {r['archive_date']}, last_modified: {r['last_modified']}")
    #
    # # Find DB export files that are missing from the S3 export
    # for row in db_rows:
    #     if row['state'] == 'ACTIVE':
    #         key = f"product-attachments/{row['product_id']}/{row['name']}"
    #         if not find_file_info(s3_file_infos, key):
    #             print(f"DB export file not found in S3 export: {key}")
