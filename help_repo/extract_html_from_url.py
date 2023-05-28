from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Set the path to your chromedriver executable
chrome_driver_path = 'path/to/chromedriver'

# Configure Chrome options
chrome_options = Options()
chrome_options.add_argument('--headless')  # Run Chrome in headless mode

# Create a new Selenium WebDriver instance
driver = webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)

# Make a GET request to the web page
def scrape_with_selenium(url):
    driver.get(url)
    # Wait for the specific element or condition to be present
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.active-filters')))
    # Get the final HTML source after JavaScript execution
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    return soup

soup = scrape_with_selenium('https://livresgg.ca/gagnants-et-finalistes-precedents')
print(soup)

# Close the WebDriver and exit
driver.quit()
