select product_file.name, product_file.create_date, product_file.update_date,
       product_file.storage_version_id, product_file_set.product_id, product_file_set.archive_date,
       product_file_set.id
from product_file
        inner join product_file_set on product_file.product_file_set_id = product_file_set.id
where product_file.state = 'ACTIVE';