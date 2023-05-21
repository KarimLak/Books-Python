import requests
from bs4 import BeautifulSoup
from rdflib import Graph, URIRef, Namespace, Literal
from rdflib.namespace import RDF, XSD
import uuid

def scrape_with_beautifulsoup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

soup = scrape_with_beautifulsoup('https://fmdoc.org/activites/prix-alvine-belisle/')

all_ul_elements = soup.find_all('ul')

g = Graph()
schema = Namespace("http://schema.org/")
books = Namespace("https://schema.org/Book")
award = 'Prix Alvine-Bélisle'

for ul_element in all_ul_elements:
    all_li_elements = ul_element.find_all('li')
    for li_element in all_li_elements:
        try:
            year = li_element.contents[0].strip()
            year_string = li_element.contents[0].strip().split('–')[0]  # splitting on the dash
            year = int(year_string) - 1  # subtracting 1 from the year
            year = str(year)  # converting it back to string
        except (AttributeError, TypeError):
            break

        author_link = li_element.find('a')
        author_name = author_link.text
        
        try:
            book_title = li_element.find('em').text
        except AttributeError:
            book_title = None

        genre_1 = 'Jeunesse'
        genre_2 = '0 à 17 ans'
        genre_3 = 'Littérature canadienne'
        langue = 'Français'

        if book_title:
            book_id = f"{uuid.uuid4()}"
            book_node = URIRef(books[book_id])
            g.add((book_node, RDF.type, schema.Book))
            g.add((book_node, schema.name, Literal(book_title, datatype=XSD.string)))
            authors = author_name.split(' et ')
            for author in authors:
                g.add((book_node, schema.author, Literal(author.strip(), datatype=XSD.string)))          
            g.add((book_node, schema.datePublished, Literal(year, datatype=XSD.gYear)))
            g.add((book_node, schema.award, Literal(award, datatype=XSD.string)))
            g.add((book_node, schema.genre, Literal(genre_1, datatype=XSD.string)))
            g.add((book_node, schema.genre, Literal(genre_2, datatype=XSD.string)))
            g.add((book_node, schema.genre, Literal(genre_3, datatype=XSD.string)))
            g.add((book_node, schema.inLanguage, Literal(langue, datatype=XSD.string)))

turtle_output = g.serialize(format="turtle")

with open("output-fmdoc.ttl", "w", encoding="utf-8") as f:
    f.write(turtle_output)
