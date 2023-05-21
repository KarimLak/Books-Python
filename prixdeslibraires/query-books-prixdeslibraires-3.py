from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import uuid
from rdflib import Graph, URIRef, Namespace, Literal
from rdflib.namespace import RDF, XSD
import csv
from difflib import SequenceMatcher

def scrape_with_selenium(url):
    service = Service(executable_path="path/to/your/chromedriver")
    driver = webdriver.Chrome(service=service)
    driver.get(url)
    time.sleep(5)
    return driver

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

def click_all_links(driver, button_texts):
    all_books_data = []
    main_url = driver.current_url
    for button_text in button_texts:
        # Navigate back to the main page before trying to locate the next button
        driver.get(main_url)
        time.sleep(5)

        button = driver.find_element(By.XPATH, f"//*[contains(text(), '{button_text}')]")
        print(f"Clicking: {button_text}")
        button.click()
        time.sleep(5)

        source = driver.page_source
        soup = BeautifulSoup(source, 'html.parser')

        links = soup.find_all('a')
        zoom_demo_links = [link for link in links if "zoom-demo" in link.get('href')]
        for index, link in enumerate(zoom_demo_links):
            href = link.get('href')
            print(href)
            book_data = scrape_book(href, button_text)
            if book_data:
                all_books_data.append(book_data)

            # Check if this is the last zoom-demo link for the category
            if index == len(zoom_demo_links) - 1:
                # Go back to the main page
                driver.back()
                time.sleep(10)

    return all_books_data



def book_data_to_rdf(book_data, graph):
    schema = Namespace("http://schema.org/")
    books = Namespace("https://schema.org/Book")

    book_id = f"{uuid.uuid4()}"
    book_node = URIRef(books[book_id])

    graph.add((book_node, RDF.type, schema.Book))

    langue = 'Français'

    if book_data['title']:
        graph.add((book_node, schema.name, Literal(book_data['title'], datatype=XSD.string)))
    if book_data['author']:
        authors = book_data['author'].split(' et ')
        for author in authors:
            g.add((book_node, schema.author, Literal(author.strip(), datatype=XSD.string)))          
    if book_data['publisher']:
        graph.add((book_node, schema.publisher, Literal(book_data['publisher'], datatype=XSD.string)))
    if book_data['summary']:
        graph.add((book_node, schema.description, Literal(book_data['summary'], datatype=XSD.string)))
    if book_data['genre']:
        graph.add((book_node, schema.genre, Literal(book_data['genre'], datatype=XSD.string)))
    if book_data['url']:
        graph.add((book_node, schema.url, Literal(book_data['url'], datatype=XSD.string)))
    if book_data['datePublished']:
        graph.add((book_node, schema.datePublished, Literal(book_data['datePublished'], datatype=XSD.string)))
    if book_data['award']:
        graph.add((book_node, schema.award, Literal(book_data['award'], datatype=XSD.string)))
    if book_data['description']:
        graph.add((book_node, schema.description, Literal(book_data['description'], datatype=XSD.string)))
    g.add((book_node, schema.inLanguage, Literal(langue, datatype=XSD.string)))

    return graph

def scrape_book(url, award):
    driver.get(url)
    time.sleep(5)

    source = driver.page_source
    soup = BeautifulSoup(source, 'html.parser')

    category_tag = soup.find('span', style='color: #000080;')
    category = category_tag.text

    title_author_publisher = category_tag.find_next('p')

    text_elements = list(title_author_publisher.stripped_strings)
    title = text_elements[0] if len(text_elements) >= 1 else None

    # New implementation to handle author and publisher names
    author = None
    publisher = None
    if len(text_elements) >= 3:
        author = text_elements[1]
        publisher = text_elements[2]
    elif len(text_elements) == 2:
        if title and title.lower() in text_elements[1].lower():
            author = None
            publisher = text_elements[1]
        else:
            author = text_elements[1]
            publisher = None

    summary_header_tag = soup.find('h3', style=lambda value: value and 'color: #003366;' in value)
    if summary_header_tag:
        summary_header = summary_header_tag.find_next_sibling('div').h3.text
    else:
        summary_header = None

    book_summary_div = soup.find('div', class_='book-summary')
    if book_summary_div:
        summary_p = book_summary_div.find('p')
        if summary_p:
            summary = summary_p.text
        else:
            summary = None
    else:
        summary = None
    
    words = award.split()

    first_word = words[0]
    if first_word.endswith('s'):
        first_word = first_word[:-1]
    award_string = first_word + " " + " ".join(words[1:])

    publishers_list = read_publishers_from_csv('./query-result.csv')
    if publisher:
        publisher = best_matching_publisher(publisher, publishers_list)
        
    book_data = {
        'category': category,
        'title': title,
        'author': author,
        'publisher': publisher,
        'summary_header': summary_header,
        'summary': summary,
        'genre': 'Essai',
        'url': url,
        'datePublished': '2022',
        'award': award_string if 'Lauréat' in award_string else None,
        'description': (award_string[1:] if award_string.startswith(' ') and 'Lauréat' not in award_string else award_string) + ' : 2023 essai',
    }

    return book_data


url = 'https://prixdeslibraires.qc.ca/categorie-essai-selection/'
button_texts = ['Préliminaire 2023', 'Finalistes 2023 essai', 'Lauréat 2023 essai']

driver = scrape_with_selenium(url)

all_books_data = click_all_links(driver, button_texts)
driver.quit()

g = Graph()

# Iterate through the book data and add it to the graph
for book_data in all_books_data:
    g = book_data_to_rdf(book_data, g)

# Serialize the graph in Turtle format
turtle_output = g.serialize(format="turtle")

# Save the output to a file
with open("output-prixdeslibraires-essai.ttl", "w", encoding="utf-8") as f:
    f.write(turtle_output)
