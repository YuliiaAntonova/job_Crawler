import pandas as pd
import scrapy
import json
import re
from urllib.parse import urlencode


class JobsSpider(scrapy.Spider):
    name = "jobs"

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
    #
    # def parse_job(self, response):
    #     site_name = response.meta['site_name']
    #     location = response.meta['location']
    #     keyword = response.meta['keyword']
    #     page = response.meta['page']
    #     position = response.meta['position']
    #     data_posted = response.meta['data_posted']
    #     script_tag = re.findall(r"_initialData=(\{.+?\});", response.text)
    #     if script_tag:
    #         json_blob = json.loads(script_tag[0])
    #         job = json_blob["jobInfoWrapperModel"]["jobInfoModel"]["jobInfoHeaderModel"]
    #
    #         yield {
    #             'site_name': site_name,
    #             'keyword': keyword,
    #             'location': location,
    #             'data_posted': data_posted,
    #             'company': job.get('companyName'),
    #             'jobTitle': job.get('jobTitle'),
    #             'jobDescription': response.css('div#jobDescriptionText').get(),
    #             'url': response.url
    #         }
    def parse_job(self, response):
        site_name = response.meta['site_name']
        location = response.meta['location']
        keyword = response.meta['keyword']
        page = response.meta['page']
        position = response.meta['position']
        data_posted = response.meta['data_posted']
        script_tag = re.findall(r"_initialData=(\{.+?\});", response.text)
        if script_tag:
            json_blob = json.loads(script_tag[0])
            job = json_blob["jobInfoWrapperModel"]["jobInfoModel"]["jobInfoHeaderModel"]

            job_item = {
                'site_name': site_name,
                'keyword': keyword,
                'location': location,
                'data_posted': data_posted,
                'company': job.get('companyName'),
                'jobTitle': job.get('jobTitle'),
                'jobDescription': response.css('div#jobDescriptionText').get(),
                'url': response.url
            }
            self.results.append(job_item)
            yield job_item

    def close(self, reason):
        # After the spider finishes, create a DataFrame and write it to a CSV file
        df = pd.DataFrame(self.results)
        df.to_csv('job_listings.csv', index=False)

