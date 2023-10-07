import time

import pandas as pd
import scrapy
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..items import GlassdoorJobItem


class GlassdoorJobListSpider(scrapy.Spider):
    name = 'glassdoor-job-list'
    allowed_domains = ['glassdoor.com']
    start_urls = ['https://www.glassdoor.com/Job']

    def __init__(self, query=None, *args, **kwargs):
        super(GlassdoorJobListSpider, self).__init__(*args, **kwargs)
        self.query = "united-states-data-engineer-jobs-SRCH_IL.0,13_IN1_KO14,27.htm?fromAge=7"
        self.jobs_scraped = 0
        self.data = []
        self.items = []
        self.itemTargetCount = 20

        # Initialize the WebDriver
        self.driver = webdriver.Chrome()

    def start_requests(self):
        urls = self.start_urls
        if self.query is not None:
            for url in urls:
                yield scrapy.Request(url="{0}/{1}".format(url, self.query), callback=self.parse)

    def parse(self, response):
        url = response.url
        time.sleep(1)

        self.driver.get(url)

        try:
            # Wait for the "Sign In" button to be clickable
            sign_in_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='sign in button']"))
            )

            # Click the "Sign In" button
            sign_in_button.click()
        except Exception as e:
            print("Error while clicking the 'Sign In' button:", e)

        try:
            # Wait for the "Close" button by its CSS classes to be clickable
            close_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.e1jbctw80.ei0fd8p1.css-1n14mz9.e1q8sty40'))
            )

            # Scroll the button into view
            actions = ActionChains(self.driver)
            actions.move_to_element(close_button).perform()

            # Click the "Close" button
            close_button.click()
        except Exception as e:
            print("Error while clicking the 'Close' button:", e)

        accept_cookies_button = self.driver.find_element(By.ID, "onetrust-accept-btn-handler")

        # Click on the "Accept Cookies" button
        accept_cookies_button.click()

        time.sleep(0.5)

        # items = []

        # start=time.time()
        lastHeight = self.driver.execute_script("return document.body.scrollHeight")

        # itemTargetCount = 23
        # TODO
        while len(self.items) < self.itemTargetCount:
            # Scroll to the bottom of the page
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

            # Find elements you want to scrape and append them to the 'items' list
            elements = self.driver.find_elements(By.CSS_SELECTOR,
                                                 '#left-column > div.JobsList_wrapper__wgimi > ul > li')

            textElements = []
            for element in elements:
                textElements.append(element)

            self.items = textElements

            if self.items:

                # find button "Show more jobs"
                button_wrapper = self.driver.find_element(By.CLASS_NAME, 'JobsList_buttonWrapper__haBp5')
                show_more_button = button_wrapper.find_element(By.CLASS_NAME,
                                                               'button_Button__meEg5.button-base_Button__9SPjH')
                show_more_button.click()

                time.sleep(5)

                try:
                    # time.sleep(0.5)
                    button = self.driver.find_element(By.CSS_SELECTOR,
                                                      'button.e1jbctw80.ei0fd8p1.css-1n14mz9.e1q8sty40')

                    # Click on the button
                    button.click()
                    # time.sleep(2)
                except:
                    time.sleep(1)

        for i in self.items:

            i.click()
            time.sleep(1)
            try:
                show_more_button = self.driver.find_element(By.CLASS_NAME, 'JobDetails_showMore__j5Z_h')
                # Click the "Show more" button to expand the job description
                show_more_button.click()
                time.sleep(0.5)
                if show_more_button:
                    print("show more ok")
            except:
                pass
                print('show more no')
                time.sleep(2)

            try:
                time.sleep(0.1)
                job_title_element = self.driver.find_element(By.CLASS_NAME, 'JobDetails_jobTitle__Rw_gn')
                # job_title = job_title_element.text
                job_title = job_title_element.text if job_title_element else ""
                company_element = self.driver.find_element(By.CSS_SELECTOR,
                                                           'div.JobDetails_jobDetailsHeader__qKuvs div.css-8wag7x')

                company = company_element.text if company_element else ""

                job_description_element = self.driver.find_element(By.CLASS_NAME,
                                                                   "JobDetails_jobDescription__6VeBn")
                job_description = job_description_element.text if job_description_element else ""

                location_element = self.driver.find_element(By.CLASS_NAME, 'JobDetails_location__MbnUM')
                location = location_element.text if location_element else ""

                salary_range_elements = self.driver.find_elements(By.CSS_SELECTOR,
                                                                  '.SalaryEstimate_rangeEstimate__mP36_')
                salary_range = salary_range_elements if salary_range_elements else ""
                # Initialize variables to store minimum and maximum salaries
                min_salary = None
                max_salary = None

                # Iterate through the salary range elements
                for element in salary_range:
                    text = element.text
                    if "The minimum salary range is" in text:
                        min_salary = text.replace("The minimum salary range is", "").strip()
                    elif "The maximum salary range is" in text:
                        max_salary = text.replace("The maximum salary range is", "").strip()

            except NoSuchElementException:
                # different html processing
                job_title = ""
                company = ""
                job_description = ""
                location = ""
                min_salary = ""
                max_salary = ""

                time.sleep(1)

            job_item = GlassdoorJobItem()

            job_item['title'] = job_title
            job_item['company'] = company
            job_item['description'] = job_description
            job_item['source'] = 'glassdoor.com'
            job_item['location'] = location
            job_item['min_salary'] = min_salary
            job_item['max_salary'] = max_salary

            self.data.append(job_item)
            yield job_item

        self.driver.quit()

    def close(self, reason):
        print(self.data)
        print(len(self.data))
        df = pd.DataFrame(self.data)
