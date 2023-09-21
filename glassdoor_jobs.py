import json

import pandas as pd
import scrapy
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from concurrent.futures import ThreadPoolExecutor
import threading


class GlassdoorJobSpider:
    name = 'glassdoor_jobs0'

    def __init__(self, *args, **kwargs):
        super(GlassdoorJobSpider, self).__init__(*args, **kwargs)
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
        self.job_urls = []
        self.result = []
        self.result_lock = threading.Lock()

    def start_requests(self):
        with open('config.json') as f:
            config = json.load(f)
            glassdoor_config = config.get('glassdoor')
            start_url = glassdoor_config.get('start_url')
            keyword = config.get('keyword')

        start_url = start_url.format(keyword=keyword)
        return start_url

    def parse(self, response):
        self.driver.get(response)
        sleep(1)

        dropdown_div = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[data-test="DATEPOSTED"]')))
        dropdown_div.click()

        last_week_button = self.driver.find_element(By.CSS_SELECTOR, 'button[value="7"]')
        last_week_button.click()
        sleep(1)

        num_pages = 2
        current_page = 1

        while current_page <= num_pages:
            job_urls_on_page = [link.get_attribute("href") for link in
                                self.driver.find_elements(By.CSS_SELECTOR, 'a[data-test="job-link"]')]

            self.job_urls.extend(job_urls_on_page)

            try:
                next_button_locator = (By.XPATH, "//button[@data-test='pagination-next']")
                next_button = self.driver.find_element(*next_button_locator)
                self.driver.execute_script("arguments[0].click();", next_button)
                current_page += 1
                sleep(1)
            except NoSuchElementException:
                print("End of pagination.")
                break

        with ThreadPoolExecutor(max_workers=4) as executor:
            list(executor.map(self.process_job_url, self.job_urls))

    def process_job_url(self, job_url):
        driver = webdriver.Chrome()
        driver.get(job_url)

        try:
            company_element = driver.find_element(By.CSS_SELECTOR, '[data-test="employer-name"]')
            company_name = company_element.text

        except:
            company_name = ''

        try:
            job_title_element = driver.find_element(By.CSS_SELECTOR, '[data-test="job-title"]')
            job_title = job_title_element.text
        except:
            job_title = ''

        try:
            location_element = driver.find_element(By.CSS_SELECTOR, '[data-test="location"]')
            location = location_element.text
        except:
            location = ''

        try:
            span_elements = driver.find_elements(By.XPATH, '//div[@class="css-1v5elnn e11nt52q2"]/span')
            # Extract the raw salary from the second span element (index 1)
            raw_salary = span_elements[1].text
        except:
            raw_salary = ''

        try:
            job_desc_element = driver.find_element(By.CLASS_NAME, "css-1lkoiaj.e1eh6fgm1")
            job_description = job_desc_element.text
        except:
            job_description = ''

        # Preprocess the raw salary using Pandas
        min_salary, max_salary, rate_type = self.preprocess_salary(raw_salary)

        # Create a GlassdoorJobItem object for the current job
        job_item = {'source': 'glassdoor.com', 'title': job_title, 'company': company_name, 'location': location,
                    'min_salary': min_salary, 'max_salary': max_salary, 'rate_type': rate_type,
                    'description': job_description, 'link': job_url}

        with self.result_lock:
            self.result.append(job_item)

        driver.quit()  # Close the WebDriver for this thread


    def preprocess_salary(self, raw_salary):
        # Preprocess the raw salary using Pandas
        salary = raw_salary.replace('Glassdoor est.', '').replace('Employer est.', '').replace('(', '').replace(')',
                                                                                                                '').replace(
            ':', '').strip()

        # Extract min and max salaries and rate type
        if '-' in salary:
            min_salary, max_salary = map(str.strip, salary.split('-'))
        else:
            min_salary = max_salary = salary

        rate_type = 'an hour' if 'Per Hour' in min_salary else 'a year'
        min_salary = min_salary.replace(' Per Hour', '').replace('k', '000').strip()
        max_salary = max_salary.replace(' Per Hour', '').replace('k', '000').strip()

        return min_salary, max_salary, rate_type

    def save_to_csv(self):
        df = pd.DataFrame(self.result)
        df = df.drop_duplicates(subset='link')
        df.to_csv('glassdoor_jobs.csv', index=False)


if __name__ == '__main__':
    spider = GlassdoorJobSpider()
    start_url = spider.start_requests()
    spider.parse(start_url)
    spider.save_to_csv()


