import pandas as pd
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import time

company_name = []
location = []
job_title = []
job_description = []


def fetch_jobs(keyword, num_pages):
    # Initialize the WebDriver
    driver = webdriver.Chrome()
    driver.set_window_size(1120, 1000)

    driver.get("https://www.glassdoor.com/Job/Home/recentActivity.htm")
    search_input = driver.find_element(By.ID, "sc.keyword")

    search_input.send_keys(keyword)
    search_input.send_keys(Keys.ENTER)
    time.sleep(2)
    wait = WebDriverWait(driver, 10)
    dropdown_div = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[data-test="DATEPOSTED"]')))
    dropdown_div.click()

    # Locate the <button> element for "Last Week" and click it
    last_week_button = driver.find_element(By.CSS_SELECTOR, 'button[value="7"]')
    last_week_button.click()
    time.sleep(4)

    # Loop through job cards
    current_page = 1

    time.sleep(3)

    while current_page <= num_pages:
        done = False
        while not done:
            job_cards_locator = (By.XPATH, "//article[@id='MainCol']//ul/li[@data-adv-type='GENERAL']")
            job_cards = driver.find_elements(*job_cards_locator)

            for card in job_cards:
                try:
                    driver.execute_script("arguments[0].click();", card)
                except:
                    pass  # Handle any exceptions that occur while clicking

                time.sleep(1)  # Optional delay if needed

                try:
                    company_name.append(driver.find_element(By.XPATH, './/div[@class="css-87uc0g e1tk4kwz1"]').text)
                    location.append(driver.find_element(By.XPATH, './/div[@class="css-56kyx5 e1tk4kwz5"]').text)
                    job_title.append(
                        driver.find_element(By.XPATH, './/div[contains(@class, "css-1vg6q84 e1tk4kwz4")]').text)
                    job_description_element = driver.find_element(By.CLASS_NAME, "jobDescriptionContent.desc")

                    # Extract the job description
                    job_description.append(job_description_element.text)
                    # Click "Show More" until all content is loaded

                    try:
                        show_more_button = driver.find_element(By.XPATH, "//div[@class='css-t3xrds e856ufb4']")
                        if show_more_button.is_displayed():
                            driver.execute_script("arguments[0].click();", show_more_button)
                            time.sleep(2)  # Wait for content to load (you can adjust the waiting time if needed)
                    except:
                        pass

                    # Wait for a short moment to allow the full job description to load
                    time.sleep(2)

                except:
                    time.sleep(5)

            done = True

        if done:
            # Print progress

            print(f"{current_page} out of {num_pages} pages done")

            # Find and click the 'next' button with explicit wait
            next_button_locator = (By.XPATH, f"//button[@data-test='pagination-link-{current_page + 1}']")
            try:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(next_button_locator))
                next_button = driver.find_element(*next_button_locator)
                driver.execute_script("arguments[0].click();", next_button)
                current_page += 1
            except NoSuchElementException:
                print(f"End of pagination. Current page: {current_page}")
                break

            time.sleep(4)  # Optional delay if needed

    df = pd.DataFrame({'company': company_name,
                       'job title': job_title,
                       'location': location,
                       'job description': job_description
                       })
    driver.quit()
    return df


def main():
    keyword = "Data Engineer"
    num_pages = 2

    print(fetch_jobs(keyword, num_pages))


if __name__ == "__main__":
    main()
