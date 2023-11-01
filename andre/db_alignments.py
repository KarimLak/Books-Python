from rdflib import Graph
from rdflib.namespace import RDF
import utils
import copy
import interdbstats_exact

from book_alignment import BookAlignment

stats_logger = utils.setup_logger('stats_logger', f'exact_stats.log')

# stats_name_author = interdbstats_exact.InterDbStatsExact(key_type="name_author", stats_logger=stats_logger)
# stats_name_author_publisher = interdbstats_exact.InterDbStatsExact(key_type="name_author_publisher", stats_logger=stats_logger)
stats_isbn = interdbstats_exact.InterDbStatsExact(key_type="isbn", stats_logger=stats_logger)
# stats_name_author_publisher_date = interdbstats_exact.InterDbStatsExact(key_type="name_author_publisher_date", stats_logger=stats_logger)
# stats_name_author_date = interdbstats_exact.InterDbStatsExact(key_type="name_author_date", stats_logger=stats_logger)

# constellations
# ----------------------------------------------------
# load the graph of constellation
g = Graph()
g.parse("../final_datasets/constellations.ttl", format="turtle")
# g.parse("data/data as of 04 august/output_constellations_updated.ttl", format="turtle")
# g.parse("output_constellations_light_extended.ttl", format="turtle")

# constellation loop
for book in g.subjects(RDF.type, utils.ns1.Book):
    book_data_raw = utils.extract_data_constellation(g, book)
    book_data_preprocessed: utils.RdfBookData = \
        utils.remove_special_chars(
            utils.remove_accents(
                utils.lower(
                    utils.remove_spaces(copy.deepcopy(book_data_raw)))))

    book_alignment_constellation = BookAlignment(url_constellation=book_data_preprocessed.url,
                                                 isbn_constellation=book_data_preprocessed.isbn,
                                                 age_range_constellation=book_data_preprocessed.age_range_int,
                                                 name=book_data_raw.book_name,  # put non preprocessed name
                                                 author=book_data_raw.book_author,
                                                 publisher=book_data_raw.publisher,
                                                 date=book_data_raw.publication_date,
                                                 uri_constellation=book_data_preprocessed.uri)

    # name_author_key = utils.create_key(book_data_preprocessed.book_name, book_data_preprocessed.book_author)
    isbn_key = book_data_preprocessed.isbn
    # name_author_publisher_key = utils.create_key(book_data_preprocessed.book_name, book_data_preprocessed.book_author, book_data_preprocessed.publisher)
    # name_author_publisher_date_key = utils.create_key(book_data_preprocessed.book_name, book_data_preprocessed.book_author, book_data_preprocessed.publisher,
    #                                                   book_data_preprocessed.publication_date)
    # name_author_date_key = utils.create_key(book_name=book_data_preprocessed.book_name,
    #                                         book_author=book_data_preprocessed.book_author,
    #                                         publication_date=book_data_preprocessed.publication_date)

    # stats_name_author.all_book_alignments[name_author_key] = copy.deepcopy(book_alignment_constellation)
    stats_isbn.all_book_alignments[isbn_key] = copy.deepcopy(book_alignment_constellation)
    # stats_name_author_publisher.all_book_alignments[name_author_publisher_key] = \
    #     copy.deepcopy(book_alignment_constellation)
    # stats_name_author_publisher_date.all_book_alignments[name_author_publisher_date_key] = \
    #     copy.deepcopy(book_alignment_constellation)
    # stats_name_author_date.all_book_alignments[name_author_date_key] = \
    #     copy.deepcopy(book_alignment_constellation)

    # stats_name_author.increment_constellation_book_number()
    stats_isbn.increment_constellation_book_number()
    # stats_name_author_publisher.increment_constellation_book_number()
    # stats_name_author_publisher_date.increment_constellation_book_number()
    # stats_name_author_date.increment_constellation_book_number()

# BNF
# ----------------------------------------------------
# reset graph
g = Graph()
g.parse("../final_datasets/bnf.ttl", format="turtle")
# g.parse("data/data as of 04 august/27jul_local_output_bnf_no_duplicates.ttl", format="turtle")
# g.parse("output_bnf_light_extended.ttl", format="turtle")

# BNF loop

for book in g.subjects(RDF.type, utils.ns1.Book):  # O(M)
    book_data_raw = utils.extract_data_bnf(g, book)
    book_data_preprocessed: utils.RdfBookData = \
        utils.remove_special_chars(
            utils.remove_accents(
                utils.lower(
                    utils.remove_spaces(
                        copy.deepcopy(book_data_raw)))))
    book_alignment_bnf = BookAlignment(url_bnf=book_data_preprocessed.url,
                                       isbn_bnf=book_data_preprocessed.isbn,
                                       age_range_bnf=book_data_preprocessed.age_range_int,
                                       uri_bnf=book_data_preprocessed.uri,
                                       name=book_data_raw.book_name,  # non preprocessed name
                                       author=book_data_raw.book_author,
                                       publisher=book_data_raw.publisher,
                                       date=book_data_raw.publication_date)

    # name_author_key = utils.create_key(book_data_preprocessed.book_name, book_data_preprocessed.book_author)
    isbn_key = book_data_preprocessed.isbn
    # name_author_publisher_key = utils.create_key(book_data_preprocessed.book_name, book_data_preprocessed.book_author, book_data_preprocessed.publisher)
    # name_author_publisher_date_key = utils.create_key(book_data_preprocessed.book_name, book_data_preprocessed.book_author, book_data_preprocessed.publisher,
    #                                                   book_data_preprocessed.publication_date)
    # name_author_date_key = utils.create_key(book_name=book_data_preprocessed.book_name,
    #                                         book_author=book_data_preprocessed.book_author,
    #                                         publication_date=book_data_preprocessed.publication_date)
    #
    # stats_name_author.align_by_key(copy.deepcopy(book_alignment_bnf), name_author_key)
    stats_isbn.align_by_key(copy.deepcopy(book_alignment_bnf), isbn_key)
    # stats_name_author_publisher.align_by_key(copy.deepcopy(book_alignment_bnf), name_author_publisher_key)
    # stats_name_author_publisher_date.align_by_key(copy.deepcopy(book_alignment_bnf), name_author_publisher_date_key)
    # stats_name_author_date.align_by_key(copy.deepcopy(book_alignment_bnf), name_author_date_key)

    # stats_name_author.increment_bnf_book_number()
    stats_isbn.increment_bnf_book_number()
    # stats_name_author_publisher.increment_bnf_book_number()
    # stats_name_author_publisher_date.increment_bnf_book_number()
    # stats_name_author_date.increment_bnf_book_number()

stats_isbn.output_csv()
# stats_name_author.output_csv()
# stats_name_author_publisher.output_csv()
# stats_name_author_publisher_date.output_csv()
# stats_name_author_date.output_csv()

# stats_name_author_publisher_date.output_rdf()

print("alignment done, computing stats ...")

stats_isbn.print_stats()
# stats_name_author.print_stats()
# stats_name_author_publisher.print_stats()
# stats_name_author_publisher_date.print_stats()
# stats_name_author_date.print_stats()
