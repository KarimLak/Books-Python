from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time

# the query you want to search
query = "Michel-Strogoff babelio"

# create a new Edge session
driver = webdriver.Edge()
driver.implicitly_wait(30)

# navigate to Google
driver.get('https://www.google.com')

# find the search box and submit query
search_box = driver.find_element(By.NAME, 'q')
search_box.send_keys(query + Keys.RETURN)

# wait for the page to load
time.sleep(5)

# click on the first link
first_link = driver.find_element(By.CSS_SELECTOR, 'div.yuRUbf > a')
first_link.click()

# wait for the new page to load
time.sleep(20)

# Parse the page source with BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Extract rating
rating = soup.select_one('.grosse_note').text.strip()
print('Average rating:', rating)

# Extract the reviews
reviews = soup.select('span[itemprop="itemReviewed"]')

for review in reviews:
    author = review.select_one('span[itemprop="name"]').text
    review_rating = review.select_one('meta[itemprop="ratingValue"]').get('content')
    date = review.select_one('meta[itemprop="datePublished"]').get('content')
    content = review.select_one('.cri_corps_critique').text.strip()
    print(f'Author: {author}\nRating: {review_rating}\nDate: {date}\nContent: {content}\n{"-"*50}\n')

# Extract the tags
tags_block = driver.find_element(By.CSS_SELECTOR, 'p.tags')

# Extract the HTML and parse it with BeautifulSoup
tags_html = tags_block.get_attribute('innerHTML')
tags_soup = BeautifulSoup(tags_html, 'html.parser')

# Now, select all anchor tags and extract the text
tags_list = [tag.text.strip() for tag in tags_soup.find_all('a')]

# Print the tags
print('Tags:', tags_list)

# Extract ratings distribution
distribution_table = soup.select('.hc_droite table tr')

ratings_distribution = {}
for row in distribution_table:
    rating_elem = row.select_one('.gris')
    reviews_elem = row.select_one('.libelle nobr')
    if rating_elem and reviews_elem:   # Check if elements exist
        rating = rating_elem.text.strip()
        number_of_reviews = reviews_elem.text.strip().split()[0]  # Split and take the first part to get rid of 'avis'
        ratings_distribution[rating] = number_of_reviews

print('Ratings distribution:')
for rating, num_reviews in ratings_distribution.items():
    print(f'{rating} star: {num_reviews} reviews')

# end the Selenium browser session
driver.quit()
