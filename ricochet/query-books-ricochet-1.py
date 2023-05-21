from bs4 import BeautifulSoup
import requests
import re
from rdflib import Graph, URIRef, Namespace, Literal
from rdflib.namespace import RDF, XSD
import uuid
import csv
from difflib import SequenceMatcher

def scrape_with_beautifulsoup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

def visit_links(base_url, relative_url):
    full_url = base_url + relative_url
    soup = scrape_with_beautifulsoup(full_url)
    return soup

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

def convert_to_rdf(g, laureates_data, url):
    schema = Namespace("http://schema.org/")
    books = Namespace("https://schema.org/Book")

    for laureate_data in laureates_data:
        if len(laureate_data) < 5:
            laureate_data = laureate_data + [''] * (5 - len(laureate_data))
        award, year, title, author, publisher = laureate_data

        book_id = f"{uuid.uuid4()}"
        book_node = URIRef(books[book_id])

        genre = 'Jeunesse'
        langue = 'Français'

        g.add((book_node, RDF.type, schema.Book))
        g.add((book_node, schema.name, Literal(title, datatype=XSD.string)))
        if (author):
            authors = author.split(' et ')
            for author in authors:
                g.add((book_node, schema.author, Literal(author.strip(), datatype=XSD.string)))                     
        g.add((book_node, schema.datePublished, Literal(year, datatype=XSD.gYear)))
        g.add((book_node, schema.publisher, Literal(publisher, datatype=XSD.string)))
        g.add((book_node, schema.award, Literal(award, datatype=XSD.string)))
        g.add((book_node, schema.genre, Literal(genre, datatype=XSD.string)))
        g.add((book_node, schema.inLanguage, Literal(langue, datatype=XSD.string)))
        g.add((book_node, schema.url, Literal(url, datatype=XSD.string)))

    turtle_output = g.serialize(format="turtle")
    return turtle_output


def extract_laureates_data(soup):
    laureates_data = []

    # Extract the award title
    if (soup.find('h1')):
        award_title = soup.find('h1').get_text().strip()

    laureates_header = soup.find('h2', string='Lauréats')
    if laureates_header:
        laureates_content = laureates_header.find_next_sibling('div', class_='field-content')

        if laureates_content:
            # Find all lines with the year followed by a colon
            laureates_lines = re.findall(r'(\d{4})\s*:\s*(.+)<br/>', str(laureates_content))

            for line in laureates_lines:
                year, book_info = line
                book_info = book_info.strip()

                # Extract title, author, and publisher
                title_match = re.search(r'<[em|i][^>]*>([^<]+)<\/[em|i]>', book_info)
                author_match = re.search(r'<\/[em|i]>\s*de\s*([^<\(]+)', book_info)
                publisher_match = re.search(r'\(([^)]+)\)', book_info)

                if not title_match or not author_match:
                    title_match = re.search(r'<a[^>]*>\s*<[em|i][^>]*>([^<]+)<\/[em|i]>', book_info)
                    author_match = re.search(r'<\/[em|i]></a>\s*de\s*([^<\(]+)', book_info)

                if not title_match or not author_match:
                    title_match = re.search(r'<a[^>]*>([^<]+)<\/a>', book_info)
                    author_match = re.search(r'<\/a>\s*de\s*([^<\(]+)', book_info)
                
                if not title_match or not author_match:
                    # Try the modified regex when the old one fails
                    title_match = re.search(r'<i>([^<]+)<\/i>', book_info)
                    author_match = re.search(r'<\/i>\s*de\s*([^<\(]+)', book_info)

                if not title_match or not author_match:
                    title_match = re.search(r'<a[^>]*><[em|i][^>]*>([^<]+)<\/[em|i]><\/a>', book_info)
                    author_match = re.search(r'<\/a>,\s*de\s*([^<\(]+)', book_info)
                    publisher_match = re.search(r'\(([^)]+)\)', book_info)

                if not title_match or not author_match:
                    title_match = re.search(r'<em>([^<]+)<\/em>', book_info)
                    author_match = re.search(r'de ([^<(]+)', book_info)
                    publisher_match = re.search(r'\(([^)]+)\)', book_info)

                if not title_match or not author_match:
                    title_match = re.search(r'<em><a[^>]*>([^<]+)<\/a><\/em>', book_info)
                    author_match = re.search(r'<\/em>\s*d[’e]\s*([^<\(]+)', book_info)

                if not title_match or not author_match:
                    title_match = re.search(r'<em>([^<]+)<\/em>', book_info)
                    author_match = re.search(r'<\/em>\s*d[’e]\s*([^<\(]+)', book_info)
                
                if not title_match or not author_match:
                    title_match = re.search(r'<a[^>]*><em>([^<]+)</em></a>', book_info)
                    author_match = re.search(r'<\/a>\s*de\s*([^<(]+)', book_info)
                    publisher_match = re.search(r'\(([^)]+)\)', book_info)

                if not title_match or not author_match:
                    title_match = re.search(r'<a[^>]*><em>([^<]+)</em></a>', book_info)
                    author_match = re.search(r"<\/a>\s*d['’]\s*([^<\(]+)", book_info)
                    publisher_match = re.search(r'\(([^)]+)\)', book_info)
                
                if not title_match or not author_match:
                     title_match = re.search(r'<em>\s*<a[^>]*>([^<]+)</a>', book_info)
                     author_match = re.search(r'<\/a></em>\s*de\s*([^<\(]+)', book_info)
                     publisher_match = re.search(r'\(([^)]+)\)', book_info)

                if not title_match or not author_match:
                    title_match = re.search(r'<em>([^<]+)</em>', book_info)
                    author_match = re.search(r"<\/em>\s*d['’]\s*([^<\(]+)", book_info)
                    publisher_match = re.search(r'\(([^)]+)\)', book_info)
                
                if not title_match or not author_match:
                    title_match = re.search(r'<em><a[^>]*>([^<]+)</a>', book_info)
                    author_match = re.search(r'<\/a>\s*<\/em>de\s*([^<\(]+)', book_info)
                    publisher_match = re.search(r'\(([^)]+)\)', book_info)
                
                if not title_match or not author_match:
                    title_match = re.search(r'<em>\s*(.*?)\s*<\/em>', book_info)
                    author_match = re.search(r'<\/em>d[’e]([^)]*)\s*\(', book_info)
                    publisher_match = re.search(r'\(([^)]+)\)', book_info)

                if not title_match or not author_match:
                    title_match = re.search(r'<em>\s*<a[^>]*>(.*?)<\/a>\s*<\/em>', book_info)
                    author_match = re.search(r'<\/em>d[’e]([^)]*)\s*\(', book_info)
                    publisher_match = re.search(r'\(([^)]+)\)', book_info)

                if not title_match or not author_match:
                    title_match = re.search(r'<i>\s*<a[^>]*>(.*?)<\/a>\s*<\/i>', book_info)
                    author_match = re.search(r'd[’e]\s*(.*?)\s*\(', book_info)
                    publisher_match = re.search(r'\(([^)]+)\)', book_info)

                if not title_match or not author_match: 
                    title_match = re.search(r'<i>\s*<a[^>]*>(.*?)<\/a>\s*<\/i>|<a[^>]*><i>(.*?)<\/i>', book_info)
                    author_match = re.search(r'\bde\s*(.*?)\s*\(', book_info)
                    publisher_match = re.search(r'\(([^)]+)\)', book_info)

                if not title_match or not author_match: 
                    title_match = re.search(r'<a[^>]*>\s*<i>\s*(.*?)\s*<\/i>\s*<\/a>|<i>\s*<a[^>]*>\s*(.*?)\s*<\/a>\s*<\/i>', book_info)
                    author_match = re.search(r'\bde\s*(.*?)\s*\(', book_info)
                    publisher_match = re.search(r'\(([^)]+)\)', book_info)

                if not title_match or not author_match: 
                    title_match = re.search(r'<a[^>]*>\s*(<i>\s*(.*?)\s*<\/i>|.*?)\s*<\/a>|<i>\s*<a[^>]*>\s*(.*?)\s*<\/a>\s*<\/i>', book_info)
                    author_match = re.search(r'\bde\s*(.*?)\s*[\(\n]', book_info)
                    publisher_match = re.search(r'\(([^)]+)\)', book_info)

                if not title_match or not author_match: 
                    title_match = re.search(r'<a[^>]*>\s*(<i>\s*(.*?)\s*<\/i>|.*?)\s*<\/a>|<i>\s*<a[^>]*>\s*(.*?)\s*<\/a>\s*<\/i>', book_info)
                    author_match = re.search(r'\b[d’e]*\s*(.*?)\s*[\(\n]', book_info)
                    publisher_match = re.search(r'\(([^)]+)\)', book_info)
                
                if not title_match or not author_match: 
                     title_match = re.search(r'<a[^>]*>\s*<i>\s*(.*?)\s*<\/i>\s*<\/a>|<i>\s*(.*?)\s*<\/i>', book_info)
                     author_match = re.search(r'\b[d’e]*\s*([\S\s]*?)\s*[\(\n]', book_info) 
                     publisher_match = re.search(r'\(([^)]+)\)', book_info)
                
                if not title_match or not author_match:
                    # Try the modified regex when the old one fails
                    author_match = re.search(r':\s*([^<]+),\s*<', book_info)
                    title_match = re.search(r'<[em|i][^>]*>([^<]+)<\/[em|i]>', book_info) 
                    if not title_match:
                        title_match = re.search(r'<a[^>]*><[em|i][^>]*>([^<]+)<\/[em|i]><\/a>', book_info)
                        publisher_match = re.search(r'\(([^)]+)\)', book_info)


                if not title_match or not author_match:
                # Split the line into separate book entries
                    books = book_info.split(' et ')
                    for book in books:
                        # Attempt to extract title, author, and publisher for each book
                        title_match = re.search(r'<i>([^<]+)<\/i>', book)
                        author_match = re.search(r'de ([^<(]+)', book)
                        publisher_match = re.search(r'\(([^)]+)\)', book)

                if title_match and author_match:
                    title = title_match.group(1)
                    author = author_match.group(1).strip()
                    publisher = publisher_match.group(1).strip() if publisher_match else None
                    if title and author:
                        laureates_data.append([award_title, year.strip(), title.strip(), author.strip(), publisher.strip() if publisher else None])

                else:
                    print(f"Could not extract book info for the line: {book_info}")
        else:
            print(f"No laureates content found for {href}")
    else:
        print(f"No laureates header found for the page at {base_url}{href}")

    return laureates_data



def process_lines(laureates_lines, laureates_data, award_title):
    for line in laureates_lines:
        year, book_info = line
        book_info = book_info.replace('\xa0', ' ')

        # Extract the part inside parentheses
        paren_match = re.search(r'\(([^)]+)\)', book_info)
        publisher = paren_match.group(1).strip() if paren_match else ''
        remaining_info = book_info.replace(f'({publisher})', '').strip() if paren_match else book_info

        # Find the author's name and title
        author_title_match = re.search(r'(.+)(?:\s+de|\s+d\')\s+(.+)', remaining_info)
        if author_title_match:
            title, author = author_title_match.groups()
            if publisher in author:
                author = author.replace(publisher, '').strip()
                laureates_data.append([award_title, year.strip(), title.strip(), author.strip(), publisher.strip()])
            else:
                laureates_data.append([award_title, year.strip(), title.strip(), author.strip(), publisher.strip()])
        else:
            # Try matching with a hyphen separator
            author_title_match_hyphen = re.search(r'(.+)\s+-\s+(.+)', remaining_info)
            if author_title_match_hyphen:
                title, author = author_title_match_hyphen.groups()
                if publisher in author:
                    author = author.replace(publisher, '').strip()
                    laureates_data.append([award_title, year.strip(), title.strip(), author.strip(), publisher.strip()])
                else:
                    laureates_data.append([award_title, year.strip(), title.strip(), author.strip(), publisher.strip()])
            else:
                # Split remaining_info using space and dash
                parts = remaining_info.split(" - ")
                if len(parts) > 1:
                    title, author = parts[-1].strip(), " - ".join(parts[:-1]).strip()
                    if publisher in author:
                        author = author.replace(publisher, '').strip()
                        laureates_data.append([award_title, year.strip(), title.strip(), author.strip(), publisher.strip()])
                    else:
                        laureates_data.append([award_title, year.strip(), title.strip(), author.strip(), publisher.strip()])
                else:
                    # If no author is found, place the book's name in the author field
                    laureates_data.append([award_title, year.strip(), remaining_info.strip(), remaining_info.strip(), publisher.strip()])

def extract_award_links(soup):
    award_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('/prix-litteraires'):
            award_links.append(href)
    return award_links

# Iterate through the pages and extract award links
base_url = 'https://www.ricochet-jeunes.org'
award_listing_url = base_url + '/prix-litteraires'
next_page = award_listing_url
all_award_links = []

while next_page:
    soup = scrape_with_beautifulsoup(next_page)
    award_links = extract_award_links(soup)
    all_award_links.extend(award_links)

    next_page_tag = soup.find('a', {'rel': 'next'})

    if next_page_tag:
        page_number = next_page_tag['href'].split('page=')[-1]
        next_page = f"{award_listing_url}?prize_id_reference=All&prize_field_prize_country=All&page={page_number}"
    else:
        next_page = None

# Process all the award links
with open("output-ricochet.ttl", "w", encoding="utf-8") as f:
    pass

g = Graph()

#all_award_links = ['/prix-litteraires/prix-alvine-belisle']

for href in all_award_links:
    url = base_url+href
    link_soup = visit_links(base_url, href)

    laureates_data = extract_laureates_data(link_soup)

    convert_to_rdf(g, laureates_data, url)

turtle_output = g.serialize(format="turtle")
with open("output-ricochet.ttl", "w", encoding="utf-8") as f:
    f.write(turtle_output)