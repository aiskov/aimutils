from csv import DictReader

from typing import List


class DbExportDto:
    def __init__(self, name: str, create_date: str, update_date: str, storage_version_id: str,
                 product_id: str, archive_date: str, product_set_id: str):

        self.name = name
        self.create_date = create_date
        self.update_date = update_date
        self.storage_version_id = storage_version_id
        self.product_id = product_id
        self.archive_date = archive_date
        self.product_set_id = product_set_id

    @staticmethod
    def from_csv(data: DictReader) -> List['DbExportDto']:
        return [
            DbExportDto(
                row['name'],
                row['create_date'],
                row['update_date'],
                row['storage_version_id'],
                row['product_id'],
                row['archive_date'],
                row['id']
            )
            for row in data
        ]
