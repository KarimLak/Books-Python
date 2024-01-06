from rdflib import Graph
from rdflib.namespace import RDF
from collections import defaultdict
import csv
from itertools import zip_longest
import utils


class IntraDBStats: # stats for 1 db
    def __init__(self, source) -> None:
        self.source = source
        self.total_book_no = 0
        self.books_without_authors = []
        self.books_without_illustrator = []
        self.books_without_illustrator_and_author = []
        self.books_without_age = []
        self.books_without_name = []
        self.books_without_publication_date = []
        self.books_without_publisher = []
        self.books_without_isbn = []
        self.books_without_isbn_and_ean = []
        self.books_without_isbn_with_ean = []
        self.isbn_doublons = defaultdict(lambda: [])
        self.ean_doublons = defaultdict(lambda: [])
        self.book_name_doublons = defaultdict(lambda: [])
        self.book_name_author_doublons = defaultdict(lambda: [])
        self.book_name_author_publisher_doublons = defaultdict(lambda: [])
        self.book_name_author_publisher_date_doublons = defaultdict(lambda: [])
        self.book_name_author_ages = defaultdict(lambda: [])

    def count(self, book_data):
        self.total_book_no += 1

        if not book_data.book_name:
            self.books_without_name.append(book_data.url)
        if not book_data.book_authors:
            self.books_without_authors.append(book_data.url)
        if not book_data.illustrator:
            self.books_without_illustrator.append(book_data.url)
        if not book_data.book_authors and not book_data.illustrator:
            self.books_without_illustrator_and_author.append(book_data.url)
        if not book_data.age_range_int:
            self.books_without_age.append(book_data.url)
        if not book_data.publication_date:
            self.books_without_publication_date.append(book_data.url)
        if not book_data.publisher:
            self.books_without_publisher.append(book_data.url)
        if not book_data.isbn or book_data.isbn == "none":
            self.books_without_isbn.append(book_data.url)
            if not book_data.ean or book_data.ean == "none":
                self.books_without_isbn_and_ean.append(book_data.url)
            else:
                self.books_without_isbn_with_ean.append(book_data.url)

        self.count_doublon_with_missing_values(book_name=str(book_data.book_name),
                                               book_authors=book_data.book_authors,
                                               age_range=book_data.age_range_int,
                                               publisher=str(book_data.publisher),
                                               publication_date=str(book_data.publication_date),
                                               isbn=book_data.isbn,
                                               ean=book_data.ean,
                                               url=book_data.url)

    def count_doublon_with_missing_values(self, book_name, book_authors, age_range, publisher, publication_date, isbn, ean, url):
        
        name_key = utils.create_key(book_name)
        self.book_name_doublons[name_key].append(url)

        print(book_authors)
        name_author_key = utils.create_key(book_name, book_authors)
        self.book_name_author_doublons[name_author_key].append(url)
        print(name_author_key)

        name_author_publisher_key = utils.create_key(book_name, book_authors, publisher)
        self.book_name_author_publisher_doublons[name_author_publisher_key].append(url)

        name_author_publisher_date_key = utils.create_key(book_name, book_authors, publisher, publication_date)
        self.book_name_author_publisher_date_doublons[name_author_publisher_date_key].append(url)

        self.isbn_doublons[isbn].append(url)

        self.ean_doublons[ean].append([isbn, url])

        self.book_name_author_ages[name_author_key].append(age_range)

    def count_doublon_without_missing_values(self, book_name, book_author, age_range, url): # old method -> generated [No Missing Values] in data folder
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
    def doublon_output_csv_ean(self, key_name, doublon_dict):
        with open(f"{self.source}_doublons_{key_name}_intra_stats.csv", "w", encoding='utf-8', newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter='{')
            writer.writerow([f"{key_name}"])
            for key in doublon_dict.keys():
                value = doublon_dict[key]
                if len(value) > 1: # more than 1 book for 1 key means there's a doublon
                    isbn_1 = value[0][0]
                    isbn_2 = value[1][0]
                    if isbn_1 == '' or isbn_2 == '':
                        writer.writerow([key] + ["undefined"] + value)
                    else:
                        writer.writerow([key] + [isbn_1==isbn_2] + value)
    def output_csv(self):
        if 1: # toggle if we want to recompute stats for intra db
            with open(f"{self.source}_intra_stats.csv", "w", encoding='utf-8', newline="") as csvfile:
                writer = csv.writer(csvfile, delimiter='{')
                writer.writerow([f"without isbn: {len(self.books_without_isbn)}",
                                 f"without isbn and ean: {len(self.books_without_isbn_and_ean)}",
                                 f"without isbn with ean: {len(self.books_without_isbn_with_ean)}",
                                 f"without name: {len(self.books_without_name)}",
                                 f"without author:{len(self.books_without_authors)}",
                                 f"without illustrator:{len(self.books_without_illustrator)}",
                                 f"without illustrator and author:{len(self.books_without_illustrator_and_author)}",
                                 f"without age {len(self.books_without_age)}",
                                 f"without publication date {len(self.books_without_publication_date)}",
                                 f"without publisher {len(self.books_without_publisher)}"])

                rows = zip_longest(self.books_without_isbn,
                                   self.books_without_isbn_and_ean,
                                   self.books_without_isbn_with_ean,
                                   self.books_without_name,
                                   self.books_without_authors,
                                   self.books_without_illustrator,
                                   self.books_without_illustrator_and_author,
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
        self.doublon_output_csv_ean("ean", self.ean_doublons)



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
                similarity = utils.jaccard(book_name_author_ages_doublons[key][0], book_name_author_ages_doublons[key][1]) # similarité entre seulement 2 doublons pour tester
                print(f"key: {key} | lists: {book_name_author_ages_doublons[key]} |  similarity between 2 lists: {similarity}")
                average_similarity += similarity
        print("average similarity between ages of same name_author", average_similarity/name_author_doublon_count)

'''
#------------------------------------
# CONSTELLATION

# load the graph of constellation
g = Graph()
g.parse("final_datasets/constellations.ttl", format="turtle")
stats_constellation = IntraDBStats(source="Constellation")

for book in g.subjects(RDF.type, utils.schema.Book):
    book_data = utils.extract_data_constellation(g, book)
    stats_constellation.count(book_data)

stats_constellation.print_stats()
stats_constellation.output_csv()


#------------------------------------
# BNF

g = Graph()
g.parse("final_datasets/bnf.ttl", format="turtle")

stats_bnf = IntraDBStats(source="BNF")

for book in g.subjects(RDF.type, utils.schema.Book):
    book_data = utils.extract_data_bnf(g, book)
    stats_bnf.count(book_data)

stats_bnf.print_stats()
stats_bnf.output_csv()


#------------------------------------
# BTLF
g = Graph()
g.parse("final_datasets/btlf_books/Graphes/grapheLivres_BTLF_EditeursConsolides.ttl", format="turtle")

stats_btlf = IntraDBStats(source="BTLF")

for book in g.subjects(RDF.type, utils.schema.Book):  # O(M)
    book_data = utils.extract_data_btlf(g, book)
    stats_btlf.count(book_data)

stats_btlf.print_stats()
stats_btlf.output_csv()
'''

#------------------------------------
# Babelio
g = Graph()
g.parse("final_datasets/babelio.ttl", format="turtle")

stats_babelio = IntraDBStats(source="Babelio")

for book in g.subjects(RDF.type, utils.schema.Book):  # O(M)
    book_data = utils.extract_data_babelio(g, book)
    stats_babelio.count(book_data)

stats_babelio.print_stats()
stats_babelio.output_csv()