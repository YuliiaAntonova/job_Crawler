import pandas as pd
import html2text
from ..items import IndeedJobItem
import re
import json
import scrapy
from urllib.parse import urlencode


class IndeedJobSpider(scrapy.Spider):
    name = "indeed_job"
    custom_settings = {
        'FEEDS': {'data/%(name)s_%(time)s.csv': {'format': 'csv', }}
    }

    def __init__(self, keyword, location,*args, **kwargs):
        super(IndeedJobSpider, self).__init__(*args, **kwargs)
        self.results = []
        self.keyword = keyword
        self.location = location

    def get_indeed_search_url(self, offset=0):
        parameters = {"q": self.keyword, "l": self.location, "filter": 0, "start": offset}
        return "https://www.indeed.com/jobs?" + urlencode(parameters)

    def start_requests(self):

        # for keyword in keyword_list:
        #     for location in location_list:
        indeed_jobs_url = self.get_indeed_search_url()
        yield scrapy.Request(url=indeed_jobs_url, callback=self.parse_search_results,
                             meta={'keyword': self.keyword, 'location': self.location, 'offset': 0})

    def parse_search_results(self, response):
        location = response.meta['location']
        keyword = response.meta['keyword']
        offset = response.meta['offset']
        script_tag = re.findall(r'window.mosaic.providerData\["mosaic-provider-jobcards"\]=(\{.+?\});', response.text)
        if script_tag is not None:
            json_blob = json.loads(script_tag[0])

            ## Extract Jobs From Search Page
            jobs_list = json_blob['metaData']['mosaicProviderJobCardsModel']['results']
            for index, job in enumerate(jobs_list):
                if job.get('jobkey') is not None:
                    job_url = 'https://www.indeed.com/m/basecamp/viewjob?viewtype=embedded&jk=' + job.get('jobkey')
                    yield scrapy.Request(url=job_url,
                                         callback=self.parse_job,
                                         meta={
                                             'keyword': self.keyword,
                                             'location': self.location,
                                             'page': round(offset / 10) + 1 if offset > 0 else 1,
                                             'position': index,
                                             'jobKey': job.get('jobkey'),
                                         })

            # Paginate Through Jobs Pages
            if offset == 0:
                meta_data = json_blob["metaData"]["mosaicProviderJobCardsModel"]["tierSummaries"]
                num_results = sum(category["jobCount"] for category in meta_data)
                if num_results > 1000:
                    num_results = 200

                for offset in range(10, num_results + 10, 10):
                    url = self.get_indeed_search_url(offset)
                    yield scrapy.Request(url=url, callback=self.parse_search_results,
                                         meta={'keyword': self.keyword, 'location': self.location, 'offset': offset})

    def parse_job(self, response):
        # location = response.meta['location']
        # keyword = response.meta['keyword']
        page = response.meta['page']
        position = response.meta['position']

        # Extract job description HTML using CSS selector
        job_description_html = response.css('div#jobDescriptionText').get()

        # Convert HTML to plain text while removing HTML tags
        h = html2text.HTML2Text()
        h.ignore_links = True  # Remove links from the text
        job_description_text = h.handle(job_description_html).strip()

        # Extract salary information using CSS selector
        salary_info = response.css('div#salaryInfoAndJobType span.css-2iqe2o::text').get()

        # Process the extracted salary information using regular expressions
        salary_match = re.search(
            r'(\$\d{1,3}(?:,\d{3})*(?:\.\d{2})? - \$\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s?(an hour|a year|a month)',
            salary_info)
        min_salary = None
        max_salary = None
        rate_type = None

        if salary_match:
            salary_group = salary_match.group(1)
            if '-' in salary_group:
                min_salary, max_salary = salary_group.split(' - ')
            else:
                min_salary = salary_group

            rate_type = salary_match.group(2)  # Capture the second group as salary_type

        script_tag = re.findall(r"_initialData=(\{.+?\});", response.text)
        if script_tag:
            json_blob = json.loads(script_tag[0])

            job = json_blob["jobInfoWrapperModel"]["jobInfoModel"]["jobInfoHeaderModel"]
            job_item = IndeedJobItem()

            job_item['title'] = job.get('jobTitle')
            job_item['company'] = job.get('companyName')
            job_item['description'] = job_description_text
            job_item['source'] = 'indeed.com'
            job_item['location'] = self.location
            job_item['min_salary'] = min_salary
            job_item['max_salary'] = max_salary
            self.results.append(job_item)
            yield job_item

    def close(self, reason):
        # After the spider finishes, create a DataFrame and write it to a CSV file
        df = pd.DataFrame(self.results)

