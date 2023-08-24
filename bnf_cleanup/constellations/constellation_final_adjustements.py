import re
import requests
from bs4 import BeautifulSoup
from rdflib import Graph, Literal, Namespace, URIRef, RDF
from concurrent.futures import ThreadPoolExecutor, as_completed

# Define the namespaces
ns1 = Namespace('http://schema.org/')
pbs = Namespace('http://www.example.org/pbs/#')

# Define a function to process a single book
def process_book(book_uri):
    # Get the constellation link
    constellation_link = g.value(book_uri, pbs.constellationLink)
    
    # Make a GET request to the constellation link
    response = requests.get(str(constellation_link))

    # Create a BeautifulSoup object and specify the parser
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the element containing the copyright date
    copyright_element = soup.find(string=re.compile(r"©\d+"))
    
    # If a copyright date is found, extract the date and update the dateEdition
    if copyright_element:
        # Extract the date with regular expression
        date = re.search(r"©(\d+)", copyright_element).group(1)

        # Remove the old dateEdition
        g.remove((book_uri, pbs.dateEdition, None))

        # Add the new dateEdition
        g.add((book_uri, pbs.dateEdition, Literal(date)))

# Load the graph
g = Graph()
g.parse("output_constellations.ttl", format="ttl")

# Get the books from the graph
books = list(g.subjects(RDF.type, ns1.Book))

# Process the books using 5 workers
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(process_book, book_uri) for book_uri in books}

    for future in as_completed(futures):
        try:
            future.result()  # get the results
        except Exception as e:
            print(f"Exception occurred: {e}")

# Save the updated graph
g.serialize(destination="output_constellations_updated.ttl", format='ttl')
