from rdflib import Namespace, Graph
from rdflib.namespace import RDF
import utils
import copy
from joblib import Parallel
import time
from interdbstats import InterDBStats
from book_alignment import BookAlignment

# define the rdf namespace
ns1 = Namespace("http://schema.org/")
pbs = Namespace("http://example.org/pbs/")

#############################################################################
# before running:
## remove old data from directory so it's not overwritten
## verifiy ratio
## verifiy n_jobs (12 because 6 cores with hyperthread)
## verify source rdf -> ctrl f : "parse")
## verify key used ->ctrlf: name_author_
## verify logfile names: time_logger and stats_logger
## verify output_csv name
## verify output_rtf name
#############################################################################

N_JOBS = 12
SIMILARITY_RATIO = 0.9
key_name = "name_author_publisher_date"

time_logger = utils.setup_logger('execution_time_logger',
                                 f'hybrid_{key_name}_ratio_{SIMILARITY_RATIO}_execution_time.log')
stats_logger = utils.setup_logger('stats_logger', f'hybrid_{key_name}_ratio_{SIMILARITY_RATIO}_stats.log')

stats = InterDBStats(key_name, time_logger, stats_logger, SIMILARITY_RATIO, N_JOBS)

# constellations
# ----------------------------------------------------

# load the graph of constellation
g = Graph()
g.parse("../final_datasets/constellations.ttl", format="turtle")
# g.parse("data/data as of 04 august/output_constellations_updated.ttl", format="turtle")
# g.parse("output_constellations_light_extended.ttl", format="turtle")

# constellation loop
for book in g.subjects(RDF.type, ns1.Book):
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

    name_author_publisher_date_key = utils.create_key(book_name=book_data_preprocessed.book_name,
                                                      book_author=book_data_preprocessed.book_author,
                                                      publisher=book_data_preprocessed.publisher,
                                                      publication_date=book_data_preprocessed.publication_date)
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
g.parse("../final_datasets/bnf.ttl", format="turtle")
# g.parse("data/data as of 04 august/27jul_local_output_bnf_no_duplicates.ttl", format="turtle")
# g.parse("output_bnf_light_extended.ttl", format="turtle")

# BNF loop

for book in g.subjects(RDF.type, ns1.Book):  # O(M)
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

    name_author_publisher_date_key = utils.create_key(book_name=book_data_preprocessed.book_name,
                                                      book_author=book_data_preprocessed.book_author,
                                                      publisher=book_data_preprocessed.publisher,
                                                      publication_date=book_data_preprocessed.publication_date)
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
g.parse("../final_datasets/lurelu.ttl", format="turtle")
with Parallel(n_jobs=N_JOBS) as parallel:
    for book in g.subjects(RDF.type, ns1.Book):  # O(M)
        book_data_raw = utils.extract_data_lurelu(g, book)
        book_data_preprocessed: utils.RdfBookData = \
            utils.remove_special_chars(
                utils.remove_accents(
                    utils.lower(
                        utils.remove_spaces(
                            copy.deepcopy(book_data_raw)))))
        book_alignment_lurelu = BookAlignment(url_lurelu=book_data_preprocessed.url,
                                              isbn_lurelu=book_data_preprocessed.isbn,
                                              uri_lurelu=book_data_preprocessed.uri,
                                              name=book_data_raw.book_name,  # non preprocessed name
                                              author=book_data_raw.book_author,
                                              publisher=book_data_raw.publisher,
                                              date=book_data_raw.publication_date)

        name_author_publisher_date_key = utils.create_key(book_name=book_data_preprocessed.book_name,
                                                          book_author=book_data_preprocessed.book_author,
                                                          publisher=book_data_preprocessed.publisher,
                                                          publication_date=book_data_preprocessed.publication_date)
        # name_author_date_key = utils.create_key(book_name=book_data.book_name,
        #                                         book_author=book_data.book_author,
        #                                         publication_date=book_data.publication_date)

        start = time.time()
        # stats.align_by_approximate_key_lurelu(book_alignment_lurelu, name_author_publisher_date_key, parallel) # toggle to test pure approx alignement with lurelu
        stats.align_hybrid_without_isbn(copy.deepcopy(book_alignment_lurelu), name_author_publisher_date_key, parallel)
        end = time.time()

        if stats.lurelu_book_number % 10 == 0:
            time_logger.info(f"book no {stats.lurelu_book_number}")
            time_logger.info(f"time elapsed 1 book {end - start}")
            time_logger.info("##################")
            time_logger.info("")

        stats.increment_lurelu_book_number()

stats.output_rdf()

stats.output_csv_lurelu()

print("alignment done, computing stats ...")
stats.print_stats()
