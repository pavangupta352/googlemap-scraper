import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

# Search query
query = "Los Angeles Roofing Companies"


options = Options()
options.add_argument("--start-maximized")
options.add_argument("--headless")

# Initialize the Chrome driver with options
s = Service('chromedriver.exe')
driver = webdriver.Chrome(service=s, options=options)
driver.get("https://www.google.com/maps")


def scroll_to_bottom(driver):
    SCROLL_PAUSE_TIME = 2

    # Get scrollable container
    container = driver.find_element(By.CSS_SELECTOR, "div[role='feed']")
    driver.execute_script(
        'arguments[0].scrollTop = arguments[0].scrollHeight', container)

    last_height = driver.execute_script(
        'return arguments[0].scrollHeight', container)

    while True:
        # Scroll down to bottom
        driver.execute_script(
            'arguments[0].scrollTop = arguments[0].scrollHeight', container)

        # Wait to load more results
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script(
            'return arguments[0].scrollHeight', container)

        # Check if the "end of list" text is present
        end_of_list = driver.find_elements(
            By.CSS_SELECTOR, "span[class='HlvSq']")
        if end_of_list:
            break

        if new_height == last_height:
            break
        last_height = new_height

    # Scroll back to top
    driver.execute_script('arguments[0].scrollTop = 0', container)


def extract_company_details(url):
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "DUwDvf")))

    company_details = {}
    company_details['organization_name'] = driver.find_element(
        By.CSS_SELECTOR, 'h1.DUwDvf').text
    print(f"Extracting details for {company_details['organization_name']}")

    try:
        website_element = driver.find_element(
            By.CSS_SELECTOR, 'a.CsEnBe[href^="http"]')
        company_details['organization_primary_domain'] = website_element.get_attribute(
            'href')
        print(
            f"Website found: {company_details['organization_primary_domain']}")
    except NoSuchElementException:
        company_details['organization_primary_domain'] = "No website"
        print("No website found.")

    try:
        address_element = driver.find_element(
            By.CSS_SELECTOR, 'button.CsEnBe[data-item-id="address"]')
        company_details['address'] = address_element.get_attribute(
            'aria-label').replace('Address: ', '')
        print(f"Address found: {company_details['address']}")
    except NoSuchElementException:
        company_details['address'] = "No address"
        print("No address found.")

    try:
        phone_element = driver.find_element(
            By.CSS_SELECTOR, 'button.CsEnBe[data-item-id^="phone"]')
        company_details['phone'] = phone_element.get_attribute(
            'aria-label').replace('Phone: ', '')
        print(f"Phone found: {company_details['phone']}")
    except NoSuchElementException:
        company_details['phone'] = "No phone number"
        print("No phone number found.")

    return company_details


# Search for the companies
search_box = driver.find_element(By.ID, "searchboxinput")
search_box.send_keys(query)
search_button = driver.find_element(By.ID, "searchbox-searchbutton")
search_button.click()

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "fontTitleLarge")))

scroll_to_bottom(driver)

company_urls = [result.get_attribute(
    'href') for result in driver.find_elements(By.CSS_SELECTOR, 'a.hfpxzc')]

# CSV File setup
csv_file = 'company_data.csv'
csv_columns = ['organization_name',
               'organization_primary_domain', 'address', 'phone']
with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    writer.writeheader()

    # Extract company details for each URL and write to CSV
    for url in company_urls:
        details = extract_company_details(url)
        writer.writerow(details)

# Close the browser
driver.quit()
print("Data extraction complete and saved to CSV.")
