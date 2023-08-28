from typing import Dict

from rdflib import Graph
from rdflib.namespace import RDF
import rdflib.namespace
import utils
import copy
from joblib import Parallel
import logging
import time
import interdbstats_approx

from andre.book_alignment import BookAlignment

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

N_JOBS = 12
SIMILARITY_RATIO = 0.9
key_name = "name_author_publisher_date"

time_logger = utils.setup_logger('execution_time_logger',
                           f'approx_{key_name}_ratio_{SIMILARITY_RATIO}_execution_time.log')
stats_logger = utils.setup_logger('stats_logger', f'approx_{key_name}_ratio_{SIMILARITY_RATIO}_stats.log')

# define the namespace
pbs = rdflib.namespace.Namespace("http://www.example.org/pbs/#")
ns1 = rdflib.namespace.Namespace("http://schema.org/")
stats_approx = interdbstats_approx.InterDbStatsApprox(key_name, stats_logger, time_logger, SIMILARITY_RATIO, N_JOBS)

# constellations
# ----------------------------------------------------


# load the graph of constellation
g = Graph()
# g.parse("../output_constellations.ttl", format="turtle")
# g.parse("data/data as of 04 august/output_constellations_updated.ttl", format="turtle")
g.parse("data/light stats/output_constellations_light_extended.ttl", format="turtle")

# constellation loop

for book in g.subjects(RDF.type, ns1.Book):
    book_data: utils.RdfBookData = \
        utils.remove_special_chars(
            utils.remove_accents(
                utils.lower(
                    utils.remove_spaces(
                        utils.extract_data_constellation(g, book)))))

    book_alignment_constellation = BookAlignment(url_constellation=book_data.url,
                                                 isbn_constellation=book_data.isbn,
                                                 age_range_constellation=book_data.age_range_int)

    # name_author_key = utils.create_key(book_name, book_author)
    # isbn_key = isbn
    # name_author_publisher_key = utils.create_key(book_name, book_author, publisher)
    name_author_publisher_date_key = utils.create_key(book_name=book_data.book_name,
                                                      book_author=book_data.book_author,
                                                      publisher=book_data.publisher,
                                                      publication_date=book_data.publication_date)
    # name_author_date_key = utils.create_key(book_name=book_data.book_name,
    #                                         book_author=book_data.book_author,
    #                                         publication_date=book_data.publication_date)

    stats_approx.all_book_alignments[name_author_publisher_date_key] = copy.deepcopy(book_alignment_constellation)

    stats_approx.increment_constellation_book_number()

print("constellation book number", stats_approx.constellation_book_number)
# BNF
# ----------------------------------------------------

# reset graph
g = Graph()
# g.parse("../output_bnf.ttl", format="turtle")
# g.parse("data/data as of 04 august/27jul_local_output_bnf_no_duplicates.ttl", format="turtle")
g.parse("data/light stats/output_bnf_light_extended.ttl", format="turtle")

# BNF loop

with Parallel(n_jobs=N_JOBS) as parallel:
    for book in g.subjects(RDF.type, ns1.Book):  # O(M)
        book_data: utils.RdfBookData = \
            utils.remove_special_chars(
                utils.remove_accents(
                    utils.lower(
                        utils.remove_spaces(
                            utils.extract_data_bnf(g, book)))))
        book_alignment_bnf = BookAlignment(url_bnf=book_data.url,
                                           isbn_bnf=book_data.isbn,
                                           age_range_bnf=book_data.age_range_int)

        # name_author_key = utils.create_key(book_name, book_author)
        # isbn_key = isbn
        # name_author_publisher_key = utils.create_key(book_name, book_author, publisher)
        # name_author_publisher_date_key = utils.create_key(book_name, book_author, publisher, publication_date)
        name_author_publisher_date_key = utils.create_key(book_name=book_data.book_name,
                                                          book_author=book_data.book_author,
                                                          publisher=book_data.publisher,
                                                          publication_date=book_data.publication_date)
        # name_author_date_key = utils.create_key(book_name=book_data.book_name,
        #                                         book_author=book_data.book_author,
        #                                         publication_date=book_data.publication_date)

        start = time.time()
        stats_approx.align_by_approximate_key_bnf(copy.deepcopy(book_alignment_bnf), name_author_publisher_date_key, parallel)
        end = time.time()
        if stats_approx.bnf_book_number % 10 == 0:
            time_logger.info(f"book no {stats_approx.bnf_book_number}")
            time_logger.info(f"time elapsed 1 book {end - start}")
            time_logger.info("##################")
            time_logger.info("")

        stats_approx.increment_bnf_book_number()

stats_approx.output_csv()
stats_approx.output_rdf()
print("alignment done, computing stats ...")
stats_approx.print_stats()
