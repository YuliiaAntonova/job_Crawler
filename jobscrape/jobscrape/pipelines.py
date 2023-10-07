import csv


class CombineResultsPipeline:
    def __init__(self):
        self.results = []

    def process_item(self, item, spider):
        self.results.append(dict(item))
        return item

    def close_spider(self, spider):
        # Combine the results from both spiders into one list
        # You can access the spider name to distinguish between the results if needed
        if spider.name in ['indeed_job', 'glassdoor-job-list']:
            csv_filename = 'combined_results.csv'
            with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['title', 'company', 'description', 'source', 'location', 'min_salary', 'max_salary']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # Write a header row if the file is empty
                if csvfile.tell() == 0:
                    writer.writeheader()

                # Write the results to the CSV file
                for result in self.results:
                    writer.writerow(result)
