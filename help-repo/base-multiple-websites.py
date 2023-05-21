from bs4 import BeautifulSoup
import requests

# Make a GET request to the web page
def scrape_with_beautifulsoup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup



soup = scrape_with_beautifulsoup('https://www.ricochet-jeunes.org/prix-litteraires/prix-farniente')
print(soup)
