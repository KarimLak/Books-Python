import rdflib


EPSILON = 0.00001

def create_key(book_name, book_author="", publisher="", publication_date=""):
    return book_name + "_" + book_author + "_" + publisher + "_" + publication_date


pbs = rdflib.namespace.Namespace("http://www.example.org/pbs/#")
ns1 = rdflib.namespace.Namespace("http://schema.org/")


def extract_data_constellation(graph, book):
    book_name = str(graph.value(book, ns1.name)) if str(graph.value(book, ns1.name)) else str(
        graph.value(book, ns1.title))  # name vs title in database
    book_author = str(graph.value(book, ns1.author))
    age_range = list(graph.objects(book, pbs.ageRange))
    age_range_int = [int(age) for age in age_range]
    url = str(graph.value(book, pbs.constellationLink))
    publication_date = str(graph.value(book, ns1.datePublished))
    publisher = str(graph.value(book, ns1.publisher))
    isbn = str(graph.value(book, ns1.isbn))
    return book_name, book_author, age_range_int, url, publication_date, publisher, isbn

def extract_data_bnf(graph, book):
    book_name = str(graph.value(book, ns1.name))
    book_author = str(graph.value(book, ns1.author))
    age_range = list(graph.objects(book, ns1.ageRange))
    age_range_int = [int(age) for age in age_range]
    url = str(graph.value(book, ns1.bnfLink))
    publication_date = str(graph.value(book, ns1.datePublished))
    publisher = str(graph.value(book, ns1.publisher))
    isbn = str(graph.value(book, ns1.isbn))
    return book_name, book_author, age_range_int, url, publication_date, publisher, isbn


def jaccard(list1, list2):
    # Find the number of common elements in both lists
    common_elements = set(list1).intersection(set(list2))
    num_common_elements = len(common_elements)

    # Find the total number of unique elements in both lists
    total_elements = set(list1).union(set(list2))
    num_total_elements = len(total_elements)

    if total_elements:
        percentage_similarity = (num_common_elements / (num_total_elements)) * 100
    else:
        percentage_similarity = 0

    return percentage_similarity