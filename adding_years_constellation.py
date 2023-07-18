import requests
from bs4 import BeautifulSoup
from rdflib import Graph, Literal, BNode
from rdflib.namespace import RDF, FOAF, XSD
import rdflib.namespace

# define the namespace
pbs = rdflib.namespace.Namespace("http://www.example.org/pbs/#")
ns1 = rdflib.namespace.Namespace("http://schema.org/")

# load the graph
g = Graph()
g.parse("output_constellations.ttl", format="turtle")

# create a graph for processed books
processed_graph = Graph()

# iterate over each book in the graph
for book in g.subjects(RDF.type, ns1.Book):
    # get the constellation link for the book
    constellationLink = g.value(book, pbs.constellationLink)

    # get the page and parse it with BeautifulSoup
    response = requests.get(constellationLink)
    soup = BeautifulSoup(response.text, 'html.parser')

    # extract the age ranges from the page
    ageRanges = []
    for index, td in enumerate(soup.find_all('td')):
        divs = td.find_all('div', recursive=True, style=lambda value: value and ('background-color:white' not in value and 'background-color:#FFFFFF' not in value))
        for div in divs:
            span = div.find('span')
            if span:
                ageRanges.append(f"{span.get_text(strip=True)} {index}")

    # append the age ranges as attributes to the book
    for ageRange in ageRanges:
        g.add((book, ns1.ageRange, Literal(ageRange)))

g.serialize(destination='output_constellation_updated.ttl', format='turtle')
