import csv
import logging

from .items import IndeedJobItem


class SaveToCsvPipeline:
    def __init__(self):
        self.csv_file = open('indeed_jobs.csv', 'w', newline='', encoding='utf-8')
        self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=[
            'company',
            'description',
            'link',
            'location',
            'max_salary',
            'min_salary',
            'rate_type',
            'source',
            'title',
        ])
        self.csv_writer.writeheader()

    def process_item(self, item, spider):

        if isinstance(item, IndeedJobItem):  # Ensure that the item is of the correct type
            row = {
                'company': item.get('company'),
                'description': item.get('description'),
                'link': item.get('link'),
                'location': item.get('location'),
                'max_salary': item.get('max_salary'),
                'min_salary': item.get('min_salary'),
                'rate_type': item.get('rate_type'),
                'source': item.get('source'),
                'title': item.get('title'),
            }

            self.csv_writer.writerow(row)
            logging.info(f"Saved item to CSV: {row}")
        else:
            logging.warning(f"Item is not an instance of GlassdoorJobItem: {item}")

    def close_spider(self, spider):
        self.csv_file.close()
