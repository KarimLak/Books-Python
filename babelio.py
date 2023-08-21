from rdflib import Graph, Literal, URIRef, Namespace, BNode
from rdflib.namespace import RDF, XSD
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
from selenium.common.exceptions import NoSuchElementException
import requests
from googleapiclient.discovery import build


cx = "14146c5573d2149dd"

# Your Google API key
api_key = "AIzaSyAn6OQgvXAsJEPiJ_QosPITVr_m2BkQD5c"

# Build a service object for interacting with the API
service = build("customsearch", "v1", developerKey=api_key)

def search(query, api_key, cse_id, **kwargs):
    service_url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'q': query,
        'key': api_key,
        'cx': cse_id
    }
    params.update(kwargs)
    response = requests.get(service_url, params=params)
    return response.json()

# Define your namespaces
ns1 = Namespace("http://schema.org/")
pbs = Namespace("http://example.org/pbs/")

# Load your existing RDF data
g = Graph()
g.parse("output_books_6.ttl", format="turtle")

# Create a new Edge session
driver = webdriver.Edge()

rating_counter = 5000  # Initialize the rating_counter variable
review_counter = 8883  # Counter for unique URI
citation_counter = 8738

log_file = open('log.txt', 'a')

# Iterate over each book
start_processing = False  # Set initial flag

# Iterate over each book
for book in g.subjects(RDF.type, ns1.Book):
    # If the book being processed matches the desired book, start processing
    if str(book) == "http://schema.org/Book9b501837-eb60-49c2-8a81-3fe16cdb1bb1":
        start_processing = True

    # If we haven't encountered the desired book yet, skip this iteration
    if not start_processing:
        continue
    try:
        # Get the book name
        book_name = g.value(book, ns1.name)
        author_name = g.value(book, ns1.author)

        if not book_name or str(book_name).strip() == '':
            continue
        
        query = str(book_name) + " " + str(author_name) + " site:babelio.com"

        # Navigate to Google
        try: # Nested try-except for handling customsearch error
            res = service.cse().list(q=query, cx=cx).execute()
        except Exception as inner_e:
            if "Unable to find the server at customsearch.googleapis.com" in str(inner_e):
                input("An error occurred connecting to customsearch.googleapis.com. Press Enter to continue...")
            else:
                raise inner_e # Raise the exception to be caught by the outer try-except block
            
        # Click on the first link
        if 'items' in res:
            first_link = res['items'][0]['link']
            if 'https://www.babelio.com/babmap' in first_link:
                continue
        else:
            log_file.write(f"Failed to find the search result link for the book: {book}\n")
            continue

        # Wait for the new page to load
        driver.get(first_link)

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
                thumbs_up = review.find('span', {'id': lambda value: value and value.startswith("myspanNB")}).text
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
            g.add((review_uri, ns1.thumbsUp, Literal(thumbs_up)))

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
        

        citations = soup.select('.post.post_con')

        for citation in citations:
            # Check if 'Page de la citation' link is present in the citation
            citation_link_elems = citation.select('.dropdown_open a')

            if any('Page de la citation' in link_elem.text for link_elem in citation_link_elems):
                # Citation sub-elements
                author_elem = citation.select_one('.entete_login a')
                date_elem = citation.select_one('.entete_date span')
                date = date_elem.text.strip() if date_elem else None
                content_elem = citation.select_one('.cri_corps_critique')

                author = author_elem.text.strip() if author_elem else None
                date = date_elem.text.strip() if date_elem else None
                content = content_elem.text.strip() if content_elem else None

                # If any of the sub-elements were missing, log the issue and skip to the next citation
                if author is None or date is None or content is None:
                    log_file.write(f"Failed to extract all citation attributes for book: {book}\n")
                    continue

                # Generate a new URI for the citation
                citation_uri = URIRef(f'http://example.org/pbs/citation{citation_counter}')

                # Link the citation to the book
                g.add((book, pbs.citation, citation_uri))

                # Add the new triples to the graph
                g.add((citation_uri, RDF.type, pbs.Citation))
                g.add((citation_uri, ns1.author, Literal(author)))
                g.add((citation_uri, ns1.datePublished, Literal(date)))
                g.add((citation_uri, ns1.text, Literal(content)))

                citation_counter += 1


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
        
        ean_elem = soup.find(text=lambda s: "EAN :" in s)
        if ean_elem:
            ean_value = ean_elem.split(":")[1].strip().split('<br')[0].strip()
        else:
            ean_value = None
            log_file.write(f"Failed to extract EAN for the book: {book}\n")
        
        if ean_value:
            g.add((book, ns1.ean, Literal(ean_value)))

    except Exception as e:
        print(f"An error occurred while processing the book {book_name} (URI: {book}): {str(e)}")

g.serialize(destination='output_books_7.ttl', format='turtle')
# End the Selenium browser session
driver.quit()

     