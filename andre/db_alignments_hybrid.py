from rdflib import Graph
from rdflib.namespace import RDF
import rdflib.namespace
import utils
import copy
from joblib import Parallel
import time
from interdbstats import InterDBStats
from bookalignment import BookAlignment

# define the rdf namespace
pbs = rdflib.namespace.Namespace("http://www.example.org/pbs/#")
ns1 = rdflib.namespace.Namespace("http://schema.org/")

#############################################################################
# before running:
## remove old data from directory so it's not overwritten
## verifiy ratio
## verifiy n_jobs (12 because 6 cores with hyperthread)
## verify source rdf (ctrl f : "parse")
## verify key used (ctrlf: name_author_
## verify logfile names: time_logger and stats_logger
## verify output_csv name
#############################################################################

N_JOBS = 12
SIMILARITY_RATIO = 0.9
key_name = "name_author_publisher_date"

time_logger = utils.setup_logger('execution_time_logger',
                           f'{key_name}_approx_{SIMILARITY_RATIO}_hybrid_execution_time_logfile.log')
stats_logger = utils.setup_logger('stats_logger', f'{key_name}_approx_{SIMILARITY_RATIO}_hybrid_stats_logfile.log')


stats = InterDBStats(key_name, time_logger, stats_logger, SIMILARITY_RATIO, N_JOBS)

# constellations
# ----------------------------------------------------

# load the graph of constellation
g = Graph()
g.parse("../output_constellations.ttl", format="turtle")
# g.parse("data/data as of 04 august/output_constellations_updated.ttl", format="turtle")
# g.parse("output_constellations_light_extended.ttl", format="turtle")

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

    name_author_publisher_date_key = utils.create_key(book_name=book_data.book_name,
                                                      book_author=book_data.book_author,
                                                      publisher=book_data.publisher,
                                                      publication_date=book_data.publication_date)
    # name_author_date_key = utils.create_key(book_name=book_data.book_name,
    #                                         book_author=book_data.book_author,
    #                                         publication_date=book_data.publication_date)

    stats.all_book_alignments[name_author_publisher_date_key] = \
        copy.deepcopy(book_alignment_constellation)

    stats.increment_constellation_book_number()

print("constellation book number", stats.constellation_book_number)
# BNF
# ----------------------------------------------------

# reset graph
g = Graph()
g.parse("../output_bnf.ttl", format="turtle")
# g.parse("data/data as of 04 august/27jul_local_output_bnf_no_duplicates.ttl", format="turtle")
# g.parse("output_bnf_light_extended.ttl", format="turtle")

# BNF loop

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

    name_author_publisher_date_key = utils.create_key(book_name=book_data.book_name,
                                                      book_author=book_data.book_author,
                                                      publisher=book_data.publisher,
                                                      publication_date=book_data.publication_date)
    # name_author_date_key = utils.create_key(book_name=book_data.book_name,
    #                                         book_author=book_data.book_author,
    #                                         publication_date=book_data.publication_date)

    start = time.time()
    stats.align_hybrid(copy.deepcopy(book_alignment_bnf), name_author_publisher_date_key)
    end = time.time()
    if stats.bnf_book_number % 10 == 0:
        time_logger.info(f"book no {stats.bnf_book_number}")
        time_logger.info(f"time elapsed 1 book {end - start}")
        time_logger.info("##################")
        time_logger.info("")

    stats.increment_bnf_book_number()



# LURELU
# ----------------------------------------------------

# reset graph
g = Graph()
g.parse("../output_lurelu.ttl", format="turtle")
with Parallel(n_jobs=N_JOBS) as parallel:
    for book in g.subjects(RDF.type, ns1.Book):  # O(M)
        book_data: utils.RdfBookData = \
            utils.remove_special_chars(
                utils.remove_accents(
                    utils.lower(
                        utils.remove_spaces(
                            utils.extract_data_lurelu(g, book)))))
        book_alignment_lurelu = BookAlignment(url_lurelu=book_data.url,
                                              isbn_lurelu=book_data.isbn)

        name_author_publisher_date_key = utils.create_key(book_name=book_data.book_name,
                                                          book_author=book_data.book_author,
                                                          publisher=book_data.publisher,
                                                          publication_date=book_data.publication_date)
        # name_author_date_key = utils.create_key(book_name=book_data.book_name,
        #                                         book_author=book_data.book_author,
        #                                         publication_date=book_data.publication_date)

        start = time.time()
        stats.align_hybrid_without_isbn(copy.deepcopy(book_alignment_lurelu), name_author_publisher_date_key, parallel)
        end = time.time()

        if stats.lurelu_book_number % 10 == 0:
            time_logger.info(f"book no {stats.lurelu_book_number}")
            time_logger.info(f"time elapsed 1 book {end - start}")
            time_logger.info("##################")
            time_logger.info("")

        # stats_name_author.increment_bnf_book_number()
        # stats_isbn.increment_bnf_book_number()
        # stats_name_author_publisher.increment_bnf_book_number()
        stats.increment_lurelu_book_number()

# stats_name_author.output_csv()
# stats_isbn.output_csv()
# stats_name_author_publisher.output_csv()
stats.output_csv()

# stats_isbn.print_stats()
# stats_name_author.print_stats()
# stats_name_author_publisher.print_stats()
stats.print_stats()
