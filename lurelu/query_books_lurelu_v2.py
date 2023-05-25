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

def remove_consecutive_characters(text, char, replace_with=''):
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
    h2_tags = soup.find_all('h2')
    if not h2_tags:
        return []

    data = []

    award_name = h2_tags.pop(0).text.strip()

    for h2_tag in h2_tags:
        raw_year = h2_tag.text.strip()
        if not re.match(r"^\d{4}$", raw_year):
            continue

        award_year = raw_year
        parent_tr = h2_tag.find_parent('tr')

        if parent_tr is None:
            continue

        next_sibling = parent_tr.find_next_sibling()

        while next_sibling and next_sibling.find('h2') is None:
            if next_sibling.name == 'tr':
                columns = next_sibling.find_all('td', valign="top")
                for column in columns:
                    p_tag = column.find('p')
                    if p_tag:
                        award = award_name
                        author = None
                        title = None
                        publisher = None
                        genre = None

                        b_tag = p_tag.find('b')
                        if b_tag:
                            genre = b_tag.text.strip()
                            next_elem = b_tag.next_sibling
                            while next_elem and not isinstance(next_elem, str):
                                next_elem = next_elem.next_sibling
                            if next_elem:
                                author = next_elem.strip()
                                if author and (author.endswith('.') or author.endswith(',')):
                                    author = author[:-1]

                        title_tag = p_tag.find('em') or p_tag.find('i')
                        if not title_tag:
                            title_tag = p_tag.find('br')
                            if title_tag:
                                title = title_tag.next_sibling.strip()
                                title_tag = title_tag.find_next('br')

                        if title_tag:
                            title = title_tag.text.strip()

                            # Extract publisher
                            publisher_candidate = title_tag.find_next_sibling('br')
                            if publisher_candidate:
                                publisher_candidate = publisher_candidate.next_sibling
                                while publisher_candidate and not isinstance(publisher_candidate, str):
                                    publisher_candidate = publisher_candidate.next_sibling

                                if publisher_candidate:
                                    publisher = publisher_candidate.strip()
                                    publisher_search = re.search(r'(?<=, ).+$', publisher)
                                    if publisher_search:
                                        publisher = publisher_search.group().strip()
                                    else:
                                        publisher_parts = [part.strip() for part in publisher.split(',') if part.strip()]
                                        if len(publisher_parts) > 1:
                                            publisher = publisher_parts[-1].strip()
                                        else:
                                            publisher = re.sub(r'[<>]', '', publisher) if publisher else None

                            # Look for the publisher after the title's closing tag, if not found earlier
                            if not publisher:
                                publisher_candidate = title_tag.next_sibling
                                while publisher_candidate and not isinstance(publisher_candidate, str):
                                    publisher_candidate = publisher_candidate.next_sibling
                                publisher = publisher_candidate.strip() if publisher_candidate else None

                        if title and publisher and title in publisher:
                            publisher = publisher.replace(title, "").strip(', ')

                        data_array = [award_name, award_year, author, title, publisher, genre, link_url]
                        data.append(data_array)
            next_sibling = next_sibling.find_next_sibling()

    return data


def visit_links(soup):
    included_links = [
        "https://www.lurelu.net/prixlitt_illojeunesse.html",
        "https://www.lurelu.net/prixlitt_espiegle.html",
        "https://www.lurelu.net/prixlitt_jeunesse-librair.html",
        "https://www.lurelu.net/prixlitt_aqpf-anel.html",
        "https://www.lurelu.net/prixlitt_gouverneur.html",
        "https://www.lurelu.net/prixlitt_culinar.html",
        "https://www.lurelu.net/prixlitt_conseildesarts.html",
        "https://www.lurelu.net/prixlitt_christie.html",
        "https://www.lurelu.net/prixlitt_palmaresCJ.html",
    ]
    all_data = []

    for link in soup.find_all('a', href=True):
        link_url = 'https://www.lurelu.net/' + link['href']

        if link_url in included_links:
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
    if len(award_data) == 7:
        award, date, author, title, publisher, b_text, link_url = award_data
    elif len(award_data) == 6:
        award, date, author, title, publisher, link_url = award_data
        b_text = ''
    if author is None:
        continue
    award = remove_consecutive_characters(award, ' ')
    award = award.replace('\n', ' ')
    award = remove_consecutive_characters(award, r' ', ' ')
    award = remove_consecutive_characters(award, '"')
    award = award.title()
    award = remove_consecutive_characters(award, ' ')
    award = remove_consecutive_characters(award, '"')
    date = remove_consecutive_characters(date, ' ')
    author = remove_consecutive_characters(author, ' ')
    if title:
        title = remove_consecutive_characters(title, ' ')
        title = remove_consecutive_characters(title, r'\n', ' ')  # Replace newline characters with a space
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
    g.add((book_node, schema.genre, Literal(b_text, datatype=XSD.string)))  # Add the new genre attribute to the RDF graph
    g.add((book_node, schema.url, Literal(link_url, datatype=XSD.string)))
    g.add((book_node, schema.inLanguage, Literal(langue, datatype=XSD.string)))

turtle_output = g.serialize(format="turtle")

with open("output-lurelu-tables.ttl", "w", encoding="utf-8") as f:
    f.write(turtle_output)
