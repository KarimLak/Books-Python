from concurrent.futures import ThreadPoolExecutor
from rdflib import Graph, Literal, Namespace, RDF
from bs4 import BeautifulSoup
import requests
import re

ns1 = Namespace('http://schema.org/')
pbs = Namespace('http://www.example.org/pbs/#')

def process_book(book):
    # Get the URL
    url = str(g.value(book, pbs.constellationLink))

    # Send HTTP request
    r = requests.get(url)
    
    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(r.content, 'html.parser')
    
    # Find the title
    title_tag = soup.find('meta', {'property': 'og:title'})
    if title_tag:
        title = title_tag['content'].split(':')[-1].strip()
        # Replace the name in the graph
        g.set((book, ns1.name, Literal(title)))
    
    # Find the copyright date and number of pages
    description = soup.body.text
    match = re.search(r"©(\d+)\.(\d+) p\.", description)
    if match:
        year, pages = match.groups()
        # Replace the dateEdition in the graph
        g.set((book, pbs.dateEdition, Literal(year)))
        # Add the numberOfPages to the graph
        g.add((book, ns1.numberOfPages, Literal(pages)))

# Load your existing graph
g = Graph()
g.parse("./output_constellations.ttl", format='turtle')
print("parsed")

# Process all books in parallel using a ThreadPool
with ThreadPoolExecutor(max_workers=5) as executor:
    books = list(g.subjects(predicate=RDF.type, object=ns1.Book))
    executor.map(process_book, books)

# Save the updated graph
g.serialize("output_constellations_updated.ttl", format='turtle')
