import requests
from bs4 import BeautifulSoup
from rdflib import Graph, URIRef, Namespace, Literal
from rdflib.namespace import RDF, XSD
import uuid
import re  # Import regular expressions module
import csv
from difflib import SequenceMatcher

def remove_consecutive_characters(text, char):
    return re.sub(char + '{2,}', char, text)

def scrape_with_beautifulsoup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

def remove_consecutive_quotes(text):
    return re.sub(r'"{2,}', '"', text)

def remove_consecutive_characters(text, char):
    if not text:
        return text

    return re.sub(char + '{2,}', char, text)

def remove_consecutive_characters(text, char, replace_with=' '):
    if not text:
        return text

    return re.sub(char + '{2,}', replace_with, text)

def read_publishers_from_csv(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        return [row[0] for row in reader]

def best_matching_publisher(publisher, publisher_list):
    best_match = publisher
    best_ratio = 0

    for candidate in publisher_list:
        ratio = SequenceMatcher(None, publisher, candidate).ratio()
        if ratio > best_ratio:
            best_match = candidate
            best_ratio = ratio

    return best_match

def extract_data(soup, link_url):
    h2_tag = soup.find('h2')
    if not h2_tag:
        return []

    award_name = h2_tag.text.strip()
    data = []

    for h5_tag in soup.find_all('h5'):
        date = h5_tag.text.strip()
        p_tag = h5_tag.find_next_sibling('p')

        if p_tag and p_tag.contents:
            author = p_tag.contents[0].rstrip(',').strip() if p_tag.contents[0] and isinstance(p_tag.contents[0], str) else None
            if author and (author.endswith('.') or author.endswith(',')):
                author = author[:-1]
            
            title_tag = p_tag.find('em') or p_tag.find('i') or p_tag.find('br')
            title = title_tag.text.strip() if title_tag else None
            
            publisher = p_tag.contents[-1].lstrip(',').strip() if p_tag.contents[-1] and isinstance(p_tag.contents[-1], str) else None

            if author:
                author = remove_consecutive_characters(author, ' ')

            if author or title or publisher:
                data.append([award_name, date, author, title, publisher, link_url])

    return data

def visit_links(soup):
    excluded_links = [
        #"https://www.lurelu.net/prixlitt_cecilegagnon.html",
        "https://www.lurelu.net/prixlitt_espiegle.html",
        "https://www.lurelu.net/prixlitt_illojeunesse.html",
        "https://www.lurelu.net/prixlitt_aqpf-anel.html",
        "https://www.lurelu.net/prixlitt_gouverneur.html",
        "https://www.lurelu.net/prixlitt_culinar.html",
        "https://www.lurelu.net/prixlitt_acelf.html",
        "https://www.lurelu.net/prixlitt_conseildesarts.html",
        "https://www.lurelu.net/prixlitt_christie.html",
        #"https://www.lurelu.net/prixlitt_desjardins.html",
        "https://www.lurelu.net/prixlitt_palmaresCJ.html",
        #"https://www.lurelu.net/prixlitt_raymondplante.html",
    ]
    all_data = []

    for link in soup.find_all('a', href=True):
        link_url = 'https://www.lurelu.net/' + link['href']
        
        if link_url not in excluded_links:
            link_soup = scrape_with_beautifulsoup(link_url)
            awards_data = extract_data(link_soup, link_url)
            all_data.extend(awards_data)

    return all_data

soup = scrape_with_beautifulsoup('https://www.lurelu.net/prixlitt.html')
all_awards_data = visit_links(soup)

g = Graph()
schema = Namespace("http://schema.org/")
books = Namespace("https://schema.org/Book")

for award_data in all_awards_data:
    award, date, author, title, publisher, link_url = award_data
    award = remove_consecutive_characters(award, ' ')
    award = award.replace('\n', ' ')
    award = remove_consecutive_characters(award, r' ', ' ')
    award = remove_consecutive_characters(award, '"')
    award = award.title()

    award = remove_consecutive_characters(award, r' ', ' ')
    award = remove_consecutive_characters(award, '"')
    date = remove_consecutive_characters(date, ' ')
    author = remove_consecutive_characters(author, ' ')
    if title:
        title = remove_consecutive_characters(title, ' ')
    if publisher:
        publisher = remove_consecutive_characters(publisher, ' ')
        publisher = remove_consecutive_characters(publisher, '"')
        publishers_list = read_publishers_from_csv('./query-result.csv')
        publisher = best_matching_publisher(publisher, publishers_list)

    genre = 'Jeunesse'
    langue = 'Français'

    book_id = f"{uuid.uuid4()}"
    book_node = URIRef(books[book_id])
    g.add((book_node, RDF.type, schema.Book))
    g.add((book_node, schema.name, Literal(title, datatype=XSD.string)))
    if (author):
        authors = author.split(' et ')
        for author in authors:
            g.add((book_node, schema.author, Literal(author.strip(), datatype=XSD.string)))              
    g.add((book_node, schema.publisher, Literal(publisher, datatype=XSD.string)))
    g.add((book_node, schema.datePublished, Literal(date, datatype=XSD.gYear)))
    g.add((book_node, schema.award, Literal(award, datatype=XSD.string)))
    g.add((book_node, schema.genre, Literal(genre, datatype=XSD.string)))  # Add the new genre attribute to the RDF graph
    g.add((book_node, schema.url, Literal(link_url, datatype=XSD.string)))
    g.add((book_node, schema.inLanguage, Literal(langue, datatype=XSD.string)))


turtle_output = g.serialize(format="turtle")

with open("output-lurelu.ttl", "w", encoding="utf-8") as f:
    f.write(turtle_output)
