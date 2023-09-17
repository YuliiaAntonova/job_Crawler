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

from ..items import GlassdoorJobItem


class GlassdoorJobSpider(scrapy.Spider):
    name = 'glassdoor_jobs0'
    start_urls = ['https://www.glassdoor.com/Job/united-states-data-engineer-jobs-SRCH_IL.0,13_IN1_KO14,27.htm?']

    def __init__(self, *args, **kwargs):
        super(GlassdoorJobSpider, self).__init__(*args, **kwargs)
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
        self.job_urls = []
        self.result = []
        self.result_lock = threading.Lock()

    def parse(self, response):
        self.driver.get(response.url)
        sleep(1)
        # Extract the job total

        dropdown_div = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[data-test="DATEPOSTED"]')))
        dropdown_div.click()

        last_week_button = self.driver.find_element(By.CSS_SELECTOR, 'button[value="7"]')
        last_week_button.click()
        sleep(1)

        num_pages = 7

        current_page = 1

        while current_page <= num_pages:
            job_urls_on_page = [link.get_attribute("href") for link in
                                self.driver.find_elements(By.CSS_SELECTOR, 'a[data-test="job-link"]')]

            self.job_urls.extend(job_urls_on_page)  # Append job URLs to the list

            print(f"Job URLs for page {current_page}:")

            try:
                next_button_locator = (By.XPATH, "//button[@data-test='pagination-next']")
                next_button = self.driver.find_element(*next_button_locator)
                self.driver.execute_script("arguments[0].click();", next_button)
                current_page += 1
                sleep(1)  # Optional delay if needed
            except NoSuchElementException:
                print("End of pagination.")
                break

        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=4) as executor:
            for job_url in self.job_urls:
                executor.submit(self.process_job_url, job_url)

    def process_job_url(self, job_url):
        driver = webdriver.Chrome()  # Each thread should have its own WebDriver instance
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

            # Extract the salary from the second span element (index 1)
            salary = span_elements[1].text
            salary = salary.replace('Glassdoor est.', '').replace('Employer est.', '').replace('(', '').replace(')', '').replace(':', '')

        except:
            salary = ''

        try:
            job_desc_element = driver.find_element(By.CLASS_NAME, "css-1lkoiaj.e1eh6fgm1")
            job_description = job_desc_element.text
        except:
            job_description = ''

        job_item = GlassdoorJobItem()
        job_item['source'] = 'glassdoor.com'
        job_item['title'] = job_title
        job_item['company'] = company_name
        job_item['location'] = location
        job_item['salary'] = salary
        job_item['description'] = job_description
        job_item['link'] = job_url

        with self.result_lock:
            self.result.append(job_item)

        driver.quit()  # Close the WebDriver for this thread

    def closed(self, reason):
        # Close the main WebDriver when the spider is closed
        self.driver.quit()

        df = pd.DataFrame(self.result)
        # df.to_csv('job_glass.csv', index=False)
