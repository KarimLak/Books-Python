from rdflib import Graph
from rdflib.namespace import RDF
import rdflib.namespace
from collections import defaultdict
import csv
from itertools import zip_longest

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
        self.book_name_doublons = defaultdict(lambda: 0)
        self.book_name_author_doublons = defaultdict(lambda: 0)
        self.book_name_author_ages = defaultdict(lambda: [])

    def count(self, book_name, book_author, age_range, url, publication_date, publisher): # pass url to find books easily
        self.total_book_no += 1
        if book_name:
            self.book_name_doublons[book_name] += 1
        else:
            self.books_without_name.append(url)
        if not book_author:
            self.books_without_authors.append(url)
        if not age_range:
            self.books_without_age.append(url)
        if not publication_date:
            self.books_without_publication_date.append(url)
        if not publisher:
            self.books_without_publisher.append(url)

        if book_name and book_author:
            name_author = book_name + "_" + book_author # key for alignment
            self.book_name_author_doublons[name_author] += 1
            self.book_name_author_ages[name_author].append(age_range)

    def count_doublons(self, dict_to_count):
        doublons_count = 0
        for key in dict_to_count:
            if dict_to_count[key] > 1:
                print(f" {key} is present {dict_to_count[key]} times")
                doublons_count += 1
        print(f"number of not unique names : {doublons_count}")
        print(f"proportion of not unique names : {doublons_count/ self.total_book_no}")
        print()
        return doublons_count

    def output_csv(self):
        with open(f"{self.source}_intra_stats.csv", "w", encoding='utf-8', newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter='{')
            # write rows & transpose OR write columns -> pandas better ?
            writer.writerow([f"without name: {len(self.books_without_name)}",
                             f"without author:{len(self.books_without_authors)}",
                             f"without age {len(self.books_without_age)}",
                             f"without publication date {len(self.books_without_publication_date)}",
                             f"without publisher {len(self.books_without_publisher)}"])

            rows = zip_longest(self.books_without_name,
                               self.books_without_authors,
                               self.books_without_age,
                               self.books_without_publication_date,
                               self.books_without_publisher)
            for row in rows:
                writer.writerow(row)

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

        '''
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
        '''


def similarity_between_lists(list1, list2):
    # Find the number of common elements in both lists
    common_elements = set(list1).intersection(set(list2))
    num_common_elements = len(common_elements)

    # Find the total number of unique elements in both lists
    total_elements = set(list1).union(set(list2))
    num_total_elements = len(total_elements)

    percentage_similarity = (num_common_elements / num_total_elements) * 100

    return percentage_similarity


stats_constellation = IntraDBStats("Constellation")

# refactor to have a reader class
for book in g.subjects(RDF.type, ns1.Book):
    book_name = str(g.value(book, ns1.name)) if str(g.value(book, ns1.name)) else str(g.value(book, ns1.title)) # name vs title in database
    book_author = str(g.value(book, ns1.author))
    age_range = list(g.objects(book, pbs.ageRange))
    age_range_int = [int(age) for age in age_range]
    url = str(g.value(book, pbs.constellationLink))
    publication_date = str(g.value(book, ns1.datePublished))
    publisher = str(g.value(book, ns1.publisher))
    stats_constellation.count(book_name, book_author, age_range_int, url, publication_date, publisher)

stats_constellation.print_stats()
stats_constellation.output_csv()

if 1:
    # reset graph
    g = Graph()
    g.parse("../output_bnf_1.ttl", format="turtle")
    g.parse("../output_bnf_2.ttl", format="turtle")

    stats_bnf = IntraDBStats("BNF")

    for book in g.subjects(RDF.type, ns1.Book): #O(M)
        book_name = str(g.value(book, ns1.name))
        book_author = str(g.value(book, ns1.author))
        age_range = str(g.value(book, ns1.ageRange))
        url = str(g.value(book, ns1.bnfLink))
        publication_date = str(g.value(book, ns1.datePublished))
        publisher = str(g.value(book, ns1.publisher))
        stats_bnf.count(book_name, book_author, age_range, url, publication_date, publisher)

    stats_bnf.print_stats()
    stats_bnf.output_csv()