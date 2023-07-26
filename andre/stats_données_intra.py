from rdflib import Graph
from rdflib.namespace import RDF
import rdflib.namespace
from collections import defaultdict
import csv
from itertools import zip_longest
from utils import *

# stats
# ---------------------------
# pourcentage livres age

# define the namespace
pbs = rdflib.namespace.Namespace("http://www.example.org/pbs/#")
ns1 = rdflib.namespace.Namespace("http://schema.org/")


# load the graph of constellation
g = Graph()
g.parse("../output_constellations.ttl", format="turtle")

list_of_BookAges = {}


class IntraDBStats: # stats for 1 db
    def __init__(self, source) -> None:
        self.source = source
        self.total_book_no = 0
        self.books_without_authors = [] # name stored
        self.books_without_age = []
        self.books_without_name = []
        self.books_without_publication_date = []
        self.books_without_publisher = []
        self.books_without_isbn = []
        self.isbn_doublons = defaultdict(lambda: [])
        self.book_name_doublons = defaultdict(lambda: [])
        self.book_name_author_doublons = defaultdict(lambda: [])
        self.book_name_author_publisher_doublons = defaultdict(lambda: [])
        self.book_name_author_publisher_date_doublons = defaultdict(lambda: [])
        self.book_name_author_ages = defaultdict(lambda: [])

    def count(self, book_name, book_author, age_range, url, publication_date, publisher, isbn): # pass url to find books easily
        self.total_book_no += 1

        if not book_name:
            self.books_without_name.append(url)
        if not book_author:
            self.books_without_authors.append(url)
        if not age_range:
            self.books_without_age.append(url)
        if not publication_date:
            self.books_without_publication_date.append(url)
        if not publisher:
            self.books_without_publisher.append(url)
        if not isbn or isbn == "none":
            self.books_without_isbn.append(url)

        self.count_doublon_with_missing_values(book_name, book_author, age_range, publisher, publication_date, isbn)

    def count_doublon_with_missing_values(self, book_name, book_author, age_range, publisher, publication_date, isbn):
        name_key = create_key(book_name)
        self.book_name_doublons[name_key].append(url)

        name_author_key = create_key(book_name,book_author)
        self.book_name_author_doublons[name_author_key].append(url)

        name_author_publisher_key = create_key(book_name,book_author, publisher)
        self.book_name_author_publisher_doublons[name_author_publisher_key].append(url)

        name_author_publisher_date_key = create_key(book_name, book_author, publisher, publication_date)
        self.book_name_author_publisher_date_doublons[name_author_publisher_date_key].append(url)

        self.isbn_doublons[isbn].append(url)

        self.book_name_author_ages[name_author_key].append(age_range)

    def count_doublon_without_missing_values(self, book_name, book_author, age_range):
        if book_name:
            self.book_name_doublons[book_name].append(url)
        if book_name and book_author:
            name_author = book_name + "_" + book_author # key for alignment
            self.book_name_author_doublons[name_author].append(url)
            self.book_name_author_ages[name_author].append(age_range)

    def count_doublons(self, dict_to_count):
        doublons_count = 0
        for key in dict_to_count:
            number_of_doublon_per_key = len(dict_to_count[key])
            if number_of_doublon_per_key > 1:
                print(f" {key} is present {number_of_doublon_per_key} times")
                doublons_count += 1
        print(f"number of not unique names : {doublons_count}")
        print(f"proportion of not unique names : {doublons_count/ self.total_book_no}")
        print()
        return doublons_count

    def doublon_output_csv(self, key_name, doublon_dict):
        with open(f"{self.source}_doublons_{key_name}_intra_stats.csv", "w", encoding='utf-8', newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter='{')
            writer.writerow([f"{key_name}"])
            for key in doublon_dict.keys():
                value = doublon_dict[key]
                if len(value) > 1: # more than 1 book for 1 key means there's a doublon
                    writer.writerow([key] + value)
    def output_csv(self):
        if 1: # toggle if we want to recompute stats for intra db
            with open(f"{self.source}_intra_stats.csv", "w", encoding='utf-8', newline="") as csvfile:
                writer = csv.writer(csvfile, delimiter='{')
                writer.writerow([f"without isbn: {len(self.books_without_isbn)}",
                                 f"without name: {len(self.books_without_name)}",
                                 f"without author:{len(self.books_without_authors)}",
                                 f"without age {len(self.books_without_age)}",
                                 f"without publication date {len(self.books_without_publication_date)}",
                                 f"without publisher {len(self.books_without_publisher)}"])

                rows = zip_longest(self.books_without_isbn,
                                   self.books_without_name,
                                   self.books_without_authors,
                                   self.books_without_age,
                                   self.books_without_publication_date,
                                   self.books_without_publisher)
                for row in rows:
                    writer.writerow(row)

        self.doublon_output_csv("name", self.book_name_doublons)
        self.doublon_output_csv("name_author", self.book_name_author_doublons)
        self.doublon_output_csv("name_author_publisher", self.book_name_author_publisher_doublons)
        self.doublon_output_csv("name_author_publisher_date", self.book_name_author_publisher_date_doublons)
        self.doublon_output_csv("isbn", self.isbn_doublons)


    def print_stats(self):
        print("---------------------------------")
        print("source = ", self.source)
        print("---------------------------------")
        print("total number of books", self.total_book_no)
        print("number of books without name", len(self.books_without_name))
        print("number of books without author", len(self.books_without_authors))
        print("number of books without age", len(self.books_without_age))

        # counting name doublons
        self.count_doublons(self.book_name_doublons)

        # counting name_author doublons
        name_author_doublon_count = self.count_doublons(self.book_name_author_doublons)


        # similarity between ages of doublons
        book_name_author_ages_doublons = {}
        average_similarity = 0
        for key in self.book_name_author_ages:
            if len(self.book_name_author_ages[key]) > 1:
                book_name_author_ages_doublons[key] = self.book_name_author_ages[key]
                similarity = similarity_between_lists(book_name_author_ages_doublons[key][0], book_name_author_ages_doublons[key][1])
                print(f"key: {key} | lists: {book_name_author_ages_doublons[key]} |  similarity between 2 lists: {similarity}")
                average_similarity += similarity
        print("average similarity between ages of same name_author", average_similarity/name_author_doublon_count)


def similarity_between_lists(list1, list2):
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


stats_constellation = IntraDBStats("Constellation")

# refactor to have a reader class
for book in g.subjects(RDF.type, ns1.Book):
    book_name, book_author, age_range_int, url, publication_date, publisher, isbn = extract_data_constellation(g, book)
    stats_constellation.count(book_name, book_author, age_range_int, url, publication_date, publisher, isbn)

stats_constellation.print_stats()
stats_constellation.output_csv()

if 1:
    # reset graph
    g = Graph()
    g.parse("../output_bnf_1.ttl", format="turtle")
    g.parse("../output_bnf_2.ttl", format="turtle")

    stats_bnf = IntraDBStats("BNF")

    for book in g.subjects(RDF.type, ns1.Book): #O(M)
        book_name, book_author, age_range_int, url, publication_date, publisher, isbn = extract_data_bnf(g, book)
        stats_bnf.count(book_name, book_author, age_range_int, url, publication_date, publisher, isbn)

    stats_bnf.print_stats()
    stats_bnf.output_csv()