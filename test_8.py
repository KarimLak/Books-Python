from rdflib import Graph, Literal, URIRef, Namespace, BNode
from rdflib.namespace import RDF, XSD
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
from selenium.common.exceptions import NoSuchElementException

# Define your namespaces
ns1 = Namespace("http://schema.org/")
pbs = Namespace("http://example.org/pbs/")

# Load your existing RDF data
g = Graph()
g.parse("output.ttl", format="turtle")

# Create a new Edge session
driver = webdriver.Edge()
driver.implicitly_wait(5)

review_counter = 500
rating_counter = 500  # Initialize the rating_counter variable
review_counter = 500  # Counter for unique URI

log_file = open('log.txt', 'a')

start_book_uri = URIRef("http://schema.org/Book0234c7c9-0e9b-44d3-881d-351f0fd6a255")
start_processing = False

# Iterate over each book
for book in g.subjects(RDF.type, ns1.Book):
    try:
        if book == start_book_uri:
            start_processing = True

        if not start_processing:
            continue

        # Get the book name
        book_name = g.value(book, ns1.name)
        author_name = g.value(book, ns1.author)
        

        query = str(book_name) + " " + str(author_name) + " site:babelio.com"

        # Navigate to Google
        driver.get('https://www.google.com')

        # Find the search box and submit query
        search_box = driver.find_element(By.NAME, 'q')
        search_box.send_keys(query + Keys.RETURN)

        # Wait for the page to load
        time.sleep(5)

        is_captcha_page = len(driver.find_elements(By.ID, "captcha-form")) > 0

        # If CAPTCHA is found, wait for it to be manually solved
        if is_captcha_page:
            print("CAPTCHA encountered. Please solve it manually and then press ENTER in the console.")
            input()

        # Click on the first link
        try:
            first_link = driver.find_element(By.CSS_SELECTOR, 'div.yuRUbf > a')
            first_link.click()
        except NoSuchElementException:
            log_file.write(f"Failed to find the search result link for the book: {book}\n")
            continue

        # Wait for the new page to load
        time.sleep(5)

        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract the reviews
        reviews = soup.select('span[itemprop="itemReviewed"]')
        
        for review in reviews:
            try:
                author = review.select_one('span[itemprop="name"]').text
                review_rating = review.select_one('meta[itemprop="ratingValue"]').get('content')
                date = review.select_one('meta[itemprop="datePublished"]').get('content')
                content = review.select_one('.cri_corps_critique').text.strip()
            except AttributeError:
                log_file.write(f"Failed to extract all review attributes for book: {book}\n")
                continue

            # Generate a new URI for the review
            review_uri = URIRef(f'http://example.org/pbs/review{review_counter}')

            # Link the review to the book
            g.add((book, pbs.review, review_uri))

            # Add the new triples to the graph
            g.add((review_uri, RDF.type, pbs.Review))
            g.add((review_uri, ns1.author, Literal(author)))
            g.add((review_uri, ns1.reviewRating, Literal(review_rating, datatype=XSD.decimal)))
            g.add((review_uri, ns1.datePublished, Literal(date, datatype=XSD.date)))
            g.add((review_uri, ns1.reviewBody, Literal(content)))

            review_counter += 1

        # Extract rating distribution
        distribution_table = soup.select('.hc_droite table tr')
        ratings_distribution = {}
        for row in distribution_table:
            try:
                rating_elem = row.select_one('.gris')
                reviews_elem = row.select_one('.libelle nobr')
                if rating_elem and reviews_elem:
                    rating = float(rating_elem.text.strip())
                    number_of_reviews = int(reviews_elem.text.strip().split()[0])
                    ratings_distribution[rating] = number_of_reviews
            except ValueError:
                print(f"Failed to parse rating or number of reviews for book: {book}")
                continue

        # Add distribution to the graph
        for rating, count in ratings_distribution.items():
            distribution_uri = URIRef(f"http://example.org/pbs/distribution{rating_counter}")
            g.add((distribution_uri, RDF.type, pbs.RatingDistribution))
            g.add((distribution_uri, pbs.ratingValue, Literal(rating, datatype=XSD.decimal)))
            g.add((distribution_uri, pbs.ratingCount, Literal(count)))
            g.add((book, pbs.reviewDistribution, distribution_uri))
            rating_counter += 1

        # Extract tags and add them as keyword attributes
        try:
            tags_block = driver.find_element(By.CSS_SELECTOR, 'p.tags')
            tags_html = tags_block.get_attribute('innerHTML')
            tags_soup = BeautifulSoup(tags_html, 'html.parser')
            tags_list = [tag.text.strip() for tag in tags_soup.find_all('a')]
        except NoSuchElementException:
            tags_list = []

        for tag in tags_list:
            g.add((book, ns1.keyword, Literal(tag)))
        
        try:
            average_rating = float(soup.select_one('.grosse_note').text.strip().replace(',', '.'))
            g.add((book, pbs.averageBabelioReview, Literal(average_rating, datatype=XSD.decimal)))
        except AttributeError:
            print(f"Failed to extract the average rating for the book: {book}")

        # Extract the press reviews
       # Extract the press reviews
        press_review_divs = soup.select('.post_con')

        for review_div in press_review_divs:
            try:
                # First, check if this div contains a "Lire la critique" link
                critique_link = review_div.select_one('a.tiny_links')
                if critique_link and 'Lire la critique sur le site' in critique_link.text:
                    # If it does, this is a press review div, so we extract the review text
                    press_review_text = review_div.select_one('.cri_corps_critique').text.strip()

                    # Extract the author of the press review
                    author = review_div.select_one('.entete_login a').text.strip()

                    # Extract the date of the press review
                    date = review_div.select_one('.entete_date span').text.strip()

                    # Extract the URL of the press review
                    url = critique_link.get('href')

                    # Create a URI for this press review
                    press_review_uri = URIRef(f"pressReview{review_counter}")

                    # Add the properties of the press review
                    g.add((press_review_uri, RDF.type, ns1.Review))
                    g.add((press_review_uri, ns1.author, Literal(author)))
                    g.add((press_review_uri, ns1.datePublished, Literal(date)))
                    g.add((press_review_uri, ns1.reviewBody, Literal(press_review_text)))
                    g.add((press_review_uri, ns1.url, Literal(url)))

                    # Link the press review to the book
                    g.add((book, pbs.pressReview, press_review_uri))

                    review_counter += 1
            except Exception as e:
                # Handle exceptions here if necessary
                pass

        # Save the updated RDF data incrementally
        g.serialize(destination='output.ttl', format='turtle')

    except Exception as e:
        print(f"An error occurred while processing the book {book_name} (URI: {book}): {str(e)}")

# End the Selenium browser session
driver.quit()

     