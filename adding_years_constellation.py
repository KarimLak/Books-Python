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

# count the number of books processed
count = 0

# iterate over each book in the graph
for book in g.subjects(RDF.type, ns1.Book):
    # get the constellation link for the book
    constellationLink = g.value(book, pbs.constellationLink)

    # if constellation link is not None, then only proceed
    if constellationLink is not None:
        # get the page and parse it with BeautifulSoup
        response = requests.get(str(constellationLink))
        soup = BeautifulSoup(response.text, 'html.parser')

        # extract the age ranges from the page
            # extract the age ranges from the page
        ageRanges = []
        for index, td in enumerate(soup.find_all('td')):
            divs = td.find_all('div', recursive=True, style=lambda value: value and 'background-color:' in value)
            for div in divs:
                color = div['style'].split('background-color:')[1].split(';')[0].strip()
                if color.lower() not in ['white', '#ffffff']:
                    span = div.find('span')
                    if span:
                        ageRanges.append(f"{span.get_text(strip=True)} {index}")

        # append the age ranges as attributes to the book
        for ageRange in ageRanges:
            processed_graph.add((book, ns1.ageRange, Literal(ageRange)))

    # add the rest of the information from the original graph to the processed graph
    for predicate, obj in g.predicate_objects(book):
        if predicate != ns1.ageRange:
            processed_graph.add((book, predicate, obj))

    # increment the count and print a message every 100 books
    count += 1
    if count % 1000 == 0:
        print(f"Processed {count} books...")
        processed_graph.serialize(destination=f'output_constellation_updated_{count}.ttl', format='turtle')

# finally, write the processed graph to the file
processed_graph.serialize(destination='output_constellation_updated_final.ttl', format='turtle')
