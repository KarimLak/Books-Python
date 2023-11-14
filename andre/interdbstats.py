from typing import Dict
from logging import Logger

from book_alignment import BookAlignment
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF
import utils
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

class InterDbStats:
    def __init__(self, key_type, stats_logger) -> None:
        self.key_type: str = key_type
        self.all_book_alignments: Dict[str, BookAlignment] = {}
        self.stats_logger: Logger = stats_logger
        self.total_book_number: int = 0
        self.constellation_book_number: int = 0
        self.bnf_book_number: int = 0
        self.alignments_number: int = 0
        self.collision_number: int = 0
        self.alignment_method: str = "abstract"
        self.SIMILARITY_RATIO = -1

    def increment_alignment_number(self):
        self.alignments_number += 1

    def increment_collision_number(self):
        self.collision_number += 1

    def increment_bnf_book_number(self):
        self.bnf_book_number += 1

    def increment_constellation_book_number(self):
        self.constellation_book_number += 1

    def is_isbn_in_alignments_bnf(self, target_isbn) -> bool:
        return self.is_isbn_in_alignments(target_isbn, "bnf")

    def is_isbn_in_alignments_constellation(self, target_isbn) -> bool:
        return self.is_isbn_in_alignments(target_isbn, "constellation")

    def is_isbn_in_alignments_constellation_bnf(self, target_isbn) -> bool:
        return self.is_isbn_in_alignments(target_isbn, "constellation_or_bnf")

    def is_isbn_in_alignments_lurelu(self, target_isbn) -> bool:
        return self.is_isbn_in_alignments(target_isbn, "lurelu")

    def is_isbn_in_alignments(self, target_isbn, source) -> bool:
        if source == "bnf":
            for book_alignment in self.all_book_alignments:
                if target_isbn == self.all_book_alignments[book_alignment].isbn_bnf:
                    return True
        elif source == "constellation":
            for book_alignment in self.all_book_alignments:
                if target_isbn == self.all_book_alignments[book_alignment].isbn_constellation:
                    return True
        elif source == "lurelu":
            for book_alignment in self.all_book_alignments:
                if target_isbn == self.all_book_alignments[book_alignment].isbn_lurelu:
                    return True
        elif source == "constellation_or_bnf":
            for book_alignment in self.all_book_alignments:
                if target_isbn == self.all_book_alignments[book_alignment].isbn_constellation or target_isbn == \
                        self.all_book_alignments[book_alignment].isbn_bnf:
                    return True
        else:
            self.stats_logger.error(f"wrong source in is_isbn_in_alignments, {source} doesn't exist")
        return False

    def print_stats(self):
        self.total_book_number = self.constellation_book_number + self.bnf_book_number
        self.stats_logger.info("------------------------------------")
        self.stats_logger.info(f"key type {self.key_type}")
        self.stats_logger.info(f"number of alignments {self.alignments_number}")
        self.stats_logger.info(f"total number of books {self.total_book_number}")
        self.stats_logger.info(f"total number of books bnf {self.bnf_book_number}")
        self.stats_logger.info(f"total number of books constellation {self.constellation_book_number}")
        self.stats_logger.info(f"total number of collisions {self.collision_number}")

        self.compute_alignment_confusion_matrix_validation()


    def plot_age_similarities_histograms(self):
        jaccard_similarity_bnf_constellation = []
        jaccard_similarity_bnf_btlf = []
        jaccard_similarity_btlf_constellation = []

        for book_key in self.all_book_alignments:
            age_bnf = self.all_book_alignments[book_key].age_range_bnf
            age_constellation = self.all_book_alignments[book_key].age_range_constellation
            age_btlf = self.all_book_alignments[book_key].age_range_btlf

            if age_bnf and age_constellation and len(age_bnf) > 0 and len(age_constellation) > 0:
                similarity = utils.jaccard(age_bnf, age_constellation)
                jaccard_similarity_bnf_constellation.append(similarity)

            if age_bnf and age_btlf and len(age_bnf) > 0 and len(age_btlf) > 0:
                similarity = utils.jaccard(age_bnf, age_btlf)
                jaccard_similarity_bnf_btlf.append(similarity)

            if age_btlf and age_constellation and len(age_btlf) > 0 and len(age_constellation) > 0:
                similarity = utils.jaccard(age_btlf, age_constellation)
                jaccard_similarity_btlf_constellation.append(similarity)

        self.plot_age_similarity_histogram(jaccard_similarity_bnf_constellation, "bnf_constellation")
        self.plot_age_similarity_histogram(jaccard_similarity_bnf_btlf, "bnf_btlf")
        self.plot_age_similarity_histogram(jaccard_similarity_btlf_constellation, "btlf_constellation")

    def plot_age_similarity_histogram(self, jaccard_similarities, title):

        pandas_similarities = pd.Series(jaccard_similarities)
        step = 5
        bin_edges = np.arange(0, 100 + step, step)
        plt.hist(pandas_similarities, bins=bin_edges, rwidth=0.5)
        plt.xlabel("similarité Jaccard en %")
        plt.ylabel("nombre d'alignements")
        plt.title(title)
        plt.show()

        average_jaccard_similarity = sum(jaccard_similarities) / len(jaccard_similarities) if len(jaccard_similarities) > 0 else 0
        print(f"average jaccard similarity between ages of {title} = {average_jaccard_similarity}")


    def compute_alignment_confusion_matrix_validation(self):

        self.stats_logger.info("----- validation set")
        isbn_equality = 0  # TP
        isbn_inequality = 0  # FP
        missing_isbn_bnf_in_negatives = 0
        missing_isbn_constellation_in_negatives = 0
        missing_isbn_constellation_in_positives = 0
        missing_isbn_bnf_in_positives = 0
        total_non_alignment = 0  # N
        total_alignment = 0  # P
        non_alignment_isbn_present = 0  # FN
        non_alignment_isbn_absent = 0  # TN
        lines_without_url = 0
        ean_no_isbn = 0
        no_ean_isbn = 0
        ean_and_isbn = 0
        no_ean_no_isbn = 0
        ean_sameAs_isbn = 0
        ean_different_isbn = 0

        for book_key in self.all_book_alignments:
            isbn_constellation = self.all_book_alignments[book_key].isbn_constellation
            isbn_bnf = self.all_book_alignments[book_key].ean_bnf if self.all_book_alignments[book_key].ean_used_to_align else self.all_book_alignments[book_key].isbn_bnf

            url_constellation = self.all_book_alignments[book_key].url_constellation
            url_bnf = self.all_book_alignments[book_key].url_bnf

            if url_bnf and url_constellation:  # proof of alignment because never missing
                total_alignment += 1
                if isbn_constellation and isbn_bnf:
                    if isbn_bnf == isbn_constellation:
                        isbn_equality += 1
                    else:
                        isbn_inequality += 1
                if not isbn_constellation:
                    missing_isbn_constellation_in_positives += 1
                if not isbn_bnf:
                    missing_isbn_bnf_in_positives += 1
            elif url_bnf and not url_constellation:  # non-alignment: only 1 bnf present
                total_non_alignment += 1
                if isbn_bnf:
                    # look if isbn present in a constellation book
                    if self.is_isbn_in_alignments_constellation(isbn_bnf):
                        non_alignment_isbn_present += 1
                    else:
                        non_alignment_isbn_absent += 1
                else:
                    missing_isbn_bnf_in_negatives += 1
            elif not url_bnf and url_constellation:
                total_non_alignment += 1
                if isbn_constellation:
                    # look if isbn present in a bnf book
                    if self.is_isbn_in_alignments_bnf(isbn_constellation):
                        non_alignment_isbn_present += 1
                    else:
                        non_alignment_isbn_absent += 1
                else:
                    # missing isbn
                    missing_isbn_constellation_in_negatives += 1
            elif self.all_book_alignments[book_key].url_lurelu:
                continue # if lurelu url, do nothing
            else:  # no url at all
                lines_without_url += 1
                self.stats_logger.info("empty line", book_key)

            # ean vs isbn
            # -------
            ean_bnf: str = str(self.all_book_alignments[book_key].ean_bnf)
            if not ean_bnf and isbn_bnf:
                no_ean_isbn += 1
            elif ean_bnf and not isbn_bnf:
                ean_no_isbn += 1
            elif not ean_bnf and not isbn_bnf:
                no_ean_no_isbn += 1
            elif not ean_bnf and not isbn_bnf:
                no_ean_no_isbn += 1
            elif ean_bnf and isbn_bnf:
                ean_and_isbn += 1
                if ean_bnf == isbn_bnf:
                    ean_sameAs_isbn +=1
                else:
                    ean_different_isbn +=1


        assert((ean_sameAs_isbn + ean_different_isbn) == ean_and_isbn)

        self.stats_logger.info(f"EAN and no ISBN {ean_no_isbn}")
        self.stats_logger.info(f"no EAN and ISBN {no_ean_isbn}")
        self.stats_logger.info(f"no EAN and no ISBN {no_ean_no_isbn}")
        self.stats_logger.info(f"EAN and ISBN {ean_and_isbn}")
        self.stats_logger.info(f"EAN == ISBN {ean_sameAs_isbn}")
        self.stats_logger.info(f"EAN != ISBN {ean_different_isbn}")
        self.stats_logger.info(f"total alignment P {total_alignment}")
        self.stats_logger.info(f"total non-alignment N {total_non_alignment}")
        self.stats_logger.info(f"lines without url {lines_without_url}")
        self.stats_logger.info(f"alignment & isbn matches TP {isbn_equality}")
        self.stats_logger.info(f"alignment & NOT isbn matches FP {isbn_inequality}")
        self.stats_logger.info(f"NON alignment & NON isbn present TN {non_alignment_isbn_absent}")
        self.stats_logger.info(f"NON alignment & isbn present FN {non_alignment_isbn_present}")
        self.stats_logger.info(f"missing isbn bnf for positives {missing_isbn_bnf_in_positives}")
        self.stats_logger.info(f"missing isbn constellation for positives {missing_isbn_constellation_in_positives}")
        self.stats_logger.info(f"missing isbn bnf for negatives {missing_isbn_bnf_in_negatives}")
        self.stats_logger.info(f"missing isbn constellation for negatives {missing_isbn_constellation_in_negatives}")

    def output_rdf(self):
        output_graph = Graph()
        output_graph.bind('ns1', utils.schema)
        output_graph.bind('pbs', utils.pbs)
        alignment_counter = 0

        for book_alignment_key in self.all_book_alignments.keys():
            alignment_counter += 1
            book_alignment: BookAlignment = self.all_book_alignments[book_alignment_key]
            alignment_uri = URIRef(f'http://example.org/pbs/alignment{alignment_counter}')
            output_graph.add((alignment_uri, RDF.type, utils.pbs.Alignment))
            if book_alignment.isbn_constellation:
                output_graph.add((alignment_uri, utils.schema.isbn_constellation, Literal(book_alignment.isbn_constellation)))
            if book_alignment.isbn_bnf:
                output_graph.add((alignment_uri, utils.schema.isbn_bnf, Literal(book_alignment.isbn_bnf)))
            if book_alignment.isbn_lurelu:
                output_graph.add((alignment_uri, utils.schema.isbn_lurelu, Literal(book_alignment.isbn_lurelu)))

            output_graph.add((alignment_uri, utils.pbs.exact_key, Literal(book_alignment_key)))
            output_graph.add((alignment_uri, utils.schema.name, Literal(book_alignment.name)))
            output_graph.add((alignment_uri, utils.schema.author, Literal(book_alignment.author)))
            output_graph.add((alignment_uri, utils.schema.datePublished, Literal(book_alignment.date)))
            output_graph.add((alignment_uri, utils.schema.publisher, Literal(book_alignment.publisher)))

            if book_alignment.uri_constellation:
                output_graph.add((alignment_uri, utils.pbs.uri_constellation, URIRef(book_alignment.uri_constellation)))
            if book_alignment.uri_bnf:
                output_graph.add((alignment_uri, utils.pbs.uri_bnf, URIRef(book_alignment.uri_bnf)))
            if book_alignment.uri_lurelu:
                output_graph.add((alignment_uri, utils.pbs.uri_lurelu, URIRef(book_alignment.uri_lurelu)))

        output_graph.serialize(destination=f"{self.alignment_method}_alignment_{self.key_type}_ratio_{self.SIMILARITY_RATIO}.ttl", format='turtle')
