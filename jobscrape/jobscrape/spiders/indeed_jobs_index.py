import pandas as pd
import scrapy
import json
import re
from urllib.parse import urlencode
import html2text
from ..items import IndeedJobItem


class JobsSpider(scrapy.Spider):
    name = "indeed_job"

    def __init__(self, *args, **kwargs):
        super(JobsSpider, self).__init__(*args, **kwargs)
        self.results = []

    def start_requests(self):
        with open("sites_config.json") as f:
            sites_config = json.load(f)

        for site_config in sites_config["sites"]:
            site_name = site_config["name"]
            url_template = site_config["url_template"]
            pagination_limit = site_config["pagination_limit"]

            for start_url in site_config["start_urls"]:
                keyword = start_url["keyword"]
                location = start_url["location"]
                data_posted = start_url.get("data_posted")  # Retrieve the 'data_posted' field

                offset = 0

                # Include the 'data_posted' field in the URL construction
                url = url_template.format(keyword=keyword, location=location, offset=offset)

                if data_posted:
                    url += f"&data_posted={data_posted}"  # Append the 'data_posted' query parameter

                yield scrapy.Request(url=url, callback=self.parse_search_results,
                                     meta={'url': url, 'site_name': site_name, 'keyword': keyword, 'location': location,
                                           'offset': offset, 'pagination_limit': pagination_limit,
                                           'data_posted': data_posted})

    def parse_search_results(self, response):
        site_name = response.meta['site_name']
        location = response.meta['location']
        keyword = response.meta['keyword']
        offset = response.meta['offset']
        pagination_limit = response.meta['pagination_limit']
        url = response.meta['url']
        data_posted = response.meta['data_posted']  # Retrieve the 'data_posted' field from meta

        script_tag = re.findall(r'window.mosaic.providerData\["mosaic-provider-jobcards"\]=(\{.+?\});', response.text)
        if script_tag:
            json_blob = json.loads(script_tag[0])

            # Paginate Through Jobs Pages
            if offset == 0:
                meta_data = json_blob["metaData"]["mosaicProviderJobCardsModel"]["tierSummaries"]
                num_results = sum(category["jobCount"] for category in meta_data)
                if num_results > pagination_limit:
                    num_results = pagination_limit

                for offset in range(10, num_results + 10, 10):

                    url = response.urljoin(urlencode({"start": offset}))

                    yield scrapy.Request(url=url, callback=self.parse_search_results,
                                         meta={'url': url, 'site_name': site_name, 'keyword': keyword,
                                               'location': location,
                                               'offset': offset, 'pagination_limit': pagination_limit,
                                               'data_posted': data_posted})  # Pass 'data_posted' to meta

            # Extract Jobs From Search Page
            jobs_list = json_blob['metaData']['mosaicProviderJobCardsModel']['results']

            for index, job in enumerate(jobs_list):
                if job.get('jobkey'):
                    job_url = 'https://www.indeed.com/m/basecamp/viewjob?viewtype=embedded&jk=' + job.get('jobkey')

                    yield scrapy.Request(url=job_url,
                                         callback=self.parse_job,
                                         meta={
                                             'site_name': site_name,
                                             'keyword': keyword,
                                             'location': location,
                                             'page': round(offset / 10) + 1 if offset > 0 else 1,
                                             'position': index,
                                             'data_posted': data_posted,
                                             'jobKey': job.get('jobkey'),

                                         })

    def parse_job(self, response):
        site_name = response.meta['site_name']
        location = response.meta['location']
        keyword = response.meta['keyword']
        page = response.meta['page']
        position = response.meta['position']
        data_posted = response.meta['data_posted']
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
        salary_type = None

        if salary_match:
            salary_group = salary_match.group(1)
            if '-' in salary_group:
                min_salary, max_salary = salary_group.split(' - ')
            else:
                min_salary = salary_group

            salary_type = salary_match.group(2)  # Capture the second group as salary_type

        script_tag = re.findall(r"_initialData=(\{.+?\});", response.text)
        if script_tag:
            json_blob = json.loads(script_tag[0])

            job = json_blob["jobInfoWrapperModel"]["jobInfoModel"]["jobInfoHeaderModel"]
            job_item = IndeedJobItem()

            job_item['source'] = 'indeed.com'
            job_item['title'] = job.get('jobTitle')
            job_item['company'] = job.get('companyName')
            job_item['location'] = location
            job_item['min_salary'] = min_salary
            job_item['max_salary'] = max_salary
            job_item['salary_type'] = salary_type
            job_item['description'] = job_description_text
            job_item['link'] = response.url
            self.results.append(job_item)
            yield job_item

    def close(self, reason):
        # After the spider finishes, create a DataFrame and write it to a CSV file
        df = pd.DataFrame(self.results)



