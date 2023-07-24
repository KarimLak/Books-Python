from rdflib import Graph
from rdflib.namespace import RDF
import rdflib.namespace
from collections import defaultdict
import scipy

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


class Stats:
    def __init__(self, source) -> None:
        self.source = source
        self.total_book_no = 0
        self.author_counter = 0
        self.age_counter = 0
        self.book_name_counter = 0
        self.book_name_doublons = defaultdict(lambda: 0)
        self.book_name_author_doublons = defaultdict(lambda: 0)
        self.book_name_author_ages = defaultdict(lambda: [])

    def count(self, book_name, book_author, age_range):
        self.total_book_no += 1
        if book_name:
            self.book_name_counter += 1
            self.book_name_doublons[book_name] += 1
        if book_author:
            self.author_counter += 1
        if age_range:
            self.age_counter += 1
        if book_name and book_author:
            name_author = book_name + "_" + book_author
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

    def print_stats(self):
        print("---------------------------------")
        print("source = ", self.source)
        print("---------------------------------")
        print("total number of books", self.total_book_no)
        print("number of books without name", self.total_book_no - self.book_name_counter)
        print("number of books without author", self.total_book_no - self.author_counter)
        print("number of books without age", self.total_book_no - self.age_counter)

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

    percentage_similarity = (num_common_elements / num_total_elements) * 100

    return percentage_similarity


stats_constellation = Stats("Constellation")

for book in g.subjects(RDF.type, ns1.Book):
    book_name = str(g.value(book, ns1.name)) if str(g.value(book, ns1.name)) else str(g.value(book, ns1.title)) # name vs title in database
    book_author = str(g.value(book, ns1.author))
    age_range = list(g.objects(book, pbs.ageRange))
    age_range_int = [int(age) for age in age_range]
    stats_constellation.count(book_name, book_author, age_range_int)

stats_constellation.print_stats()

if 0:
    # reset graph
    g = Graph()
    g.parse("../output_bnf_1.ttl", format="turtle")
    g.parse("../output_bnf_2.ttl", format="turtle")

    stats_bnf = Stats("BNF")

    for book in g.subjects(RDF.type, ns1.Book): #O(M)
        book_name = str(g.value(book, ns1.title))
        book_author = str(g.value(book, ns1.author))
        age_range = str(g.value(book, ns1.publicDestinataire))
        stats_bnf.count(book_name, book_author, age_range)

    stats_bnf.print_stats()