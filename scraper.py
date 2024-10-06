import json
import os
from urllib.parse import urlencode

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from database import create_database, save_to_database

# Retry settings
MAX_RETRIES = 3
RETRY_WAIT = 5  # seconds to wait before retrying
# Load environment variables
SCRAPER_API_KEY = os.getenv("SCRAPER_API_KEY", "XXXXXX")
SCRAPER_API_URL = os.getenv("PROXY_URL","http://api.scraperapi.com/?")
URL = os.getenv("SCRAPER_URL", "https://steamcommunity.com/market/search?appid=730")
MAX_PAGES = int(os.getenv("SCRAPER_MAX_PAGES", 10))


def get_scraperapi_url(url):
    """
        Converts url into API request for ScraperAPI.
    """
    payload = {'api_key': SCRAPER_API_KEY, 'url': url}
    proxy_url = SCRAPER_API_URL + urlencode(payload)
    return proxy_url

service = Service("/usr/local/bin/chromedriver.exe")
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(service=service, options=chrome_options)

# Initialize the WebDriver with ScraperAPI proxy
def get_driver_with_scraperapi(url):
    driver.get(get_scraperapi_url(url))
    return driver

# Initialize the WebDriver
def get_driver(url):
    return driver.get(url)

# Retry mechanism function
def retry(func, *args, **kwargs):
    retries = 0
    while retries < MAX_RETRIES:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            retries += 1
            print(f"Error: {e}. Retrying {retries}/{MAX_RETRIES}...")
            if retries < MAX_RETRIES:
                time.sleep(RETRY_WAIT)
            else:
                print("Max retries reached. Skipping this task.")
                return None

# Function to wait for the page to fully load
def wait_for_page_load(inp_driver):
    WebDriverWait(inp_driver, 20).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

# Scrape the home page or category listings to get product links
def get_product_links(inp_driver, max_items=5):
    WebDriverWait(inp_driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a.market_listing_row_link"))
    )
    product_elements = inp_driver.find_elements(By.CSS_SELECTOR, "a.market_listing_row_link")
    product_links_d = [element.get_attribute('href') for element in product_elements[:max_items]]
    return product_links_d

# Function to scrape buy and sell prices from the product page
def scrape_item_prices(inp_driver, url):
    inp_driver.get(url)
    retry(wait_for_page_load, inp_driver)
    time.sleep(5)  # Wait for additional time to ensure all elements are fully loaded

    try:
        sell_price = retry(driver.find_element, By.XPATH, '//*[@id="market_commodity_forsale"]/span[2]').text
        sell_unit = retry(driver.find_element, By.XPATH, '//*[@id="market_commodity_forsale"]/span[1]').text
    except Exception as e:
        print(f"Error extracting sell price from {url}")
        sell_price = ""
        sell_unit = ""

    try:
        buy_price = retry(driver.find_element, By.XPATH, '//*[@id="market_commodity_buyrequests"]/span[2]').text
        buy_unit = retry(driver.find_element, By.XPATH, '//*[@id="market_commodity_buyrequests"]/span[1]').text
    except Exception as e:
        print(f"Error extracting buy price from {url}")
        buy_price = ""
        buy_unit = ""

    recent_activity = []
    try:
        recent_activity_section = retry(WebDriverWait(driver, 30).until,
                                        EC.presence_of_element_located((By.CSS_SELECTOR, "#market_activity_block")))
        recent_activity_rows = recent_activity_section.find_elements(By.CLASS_NAME, "market_activity_line_item")
        for row in recent_activity_rows:
            columns = row.find_elements(By.CLASS_NAME, "market_activity_cell")
            if len(columns) == 3:
                activity_type = row.find_element(By.CLASS_NAME, "market_activity_action").text
                price = columns[1].text
                recent_activity.append({
                    "activity_type": activity_type,
                    "price": price
                })
    except Exception as e:
        print(f"Error extracting recent activity from {url}")

    return {'buy_price': buy_price, 'buy_quantity': buy_unit, 'sell_price': sell_price, 'sell_quantity': sell_unit,
            'url': url, 'recent_activity': json.dumps(recent_activity)}

# Function to click the "Next" button and go to the next page
def click_next_button(inp_driver):
    try:
        next_button = retry(WebDriverWait(driver, 20).until, EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Next')]")))
        inp_driver.execute_script("arguments[0].scrollIntoView();", next_button)
        inp_driver.execute_script("arguments[0].click();", next_button)
        print("Successfully clicked the Next button.")
        time.sleep(5)  # Add delay for the next page to load
        return True
    except Exception as e:
        print(f"Error clicking next button: {e}")
        return False

# Example usage to scrape multiple products and handle pagination
if __name__ == "__main__":
    create_database()
    try:
        get_driver(URL)

        max_pages =MAX_PAGES
        current_page = 1

        while current_page <= max_pages:
            print(f"Scraping page {current_page}...")

            product_links = retry(get_product_links, driver, max_items=10)

            if not product_links:
                print(f"Failed to get product links on page {current_page}.")
                break

            for product_link in product_links:
                driver.execute_script(f"window.open('{product_link}', '_blank');")
                driver.switch_to.window(driver.window_handles[-1])

                products = retry(scrape_item_prices, driver, product_link)
                if products:
                    save_to_database(products)

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            if not click_next_button(driver):
                break

            current_page += 1

    finally:
        driver.quit()
