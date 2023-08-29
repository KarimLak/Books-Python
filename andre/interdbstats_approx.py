import time
from logging import Logger
from joblib import delayed
from book_alignment import BookAlignment
import utils
import csv
from interdbstats_exact import InterDbStatsExact


class InterDbStatsApprox(InterDbStatsExact):
    def __init__(self, key_type, stats_logger, time_logger, SIMILARITY_RATIO, N_JOBS) -> None:
        super().__init__(key_type, stats_logger)
        self.time_logger: Logger = time_logger
        self.stats_logger: Logger = stats_logger
        self.N_JOBS: int = N_JOBS
        self.SIMILARITY_RATIO: int = SIMILARITY_RATIO
        self.alignment_method = "approx"

    def align_by_approximate_key_bnf(self, book_alignment, book_key, parallel):
        keys_to_check = list(self.all_book_alignments.keys())
        start_key_finding = time.time()
        batch_size = int(len(keys_to_check) / self.N_JOBS) + 1
        similar_keys_list = parallel(
            delayed(utils.is_key_close_enough_to_another_key)(book_key, keys_to_check[i:i + batch_size],
                                                              self.SIMILARITY_RATIO) for i in
            range(0, len(keys_to_check), batch_size))
        end_key_finding = time.time()
        if self.bnf_book_number % 10 == 0:
            self.time_logger.info(f"time elapsed key finding {end_key_finding - start_key_finding}")
        max_ratio = 0
        best_key = ""
        for key, ratio in similar_keys_list:
            if key:
                if ratio > max_ratio:
                    best_key = key
                    max_ratio = ratio
        if best_key:
            if not self.all_book_alignments[best_key].url_bnf:  # not a collision: bnf data not present
                self.all_book_alignments[best_key].align_bnf(isbn_bnf=book_alignment.isbn_bnf,
                                                             url_bnf=book_alignment.url_bnf,
                                                             similarity_ratio_bnf=max_ratio,
                                                             uri_bnf=book_alignment.uri_bnf,
                                                             key_used_to_align_bnf=book_key)
                self.increment_alignment_number()

            else:
                self.increment_collision_number()  # increase if bnf data already present: doublon inside bnf
        else:
            self.all_book_alignments[book_key] = book_alignment  # bnf data gets into the dict without alignment

    def output_csv(self):
        with open(f"{self.alignment_method}_alignment_{self.key_type}_ratio_{self.SIMILARITY_RATIO}.csv", "w",
                  encoding='utf-8',
                  newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter='{')
            writer.writerow(["key",
                             "key used to align bnf",
                             "similarity ratio",
                             "isbn_constellation",
                             "isbn_bnf",
                             "age_range_constellation",
                             "age_range_bnf",
                             "url_constellation",
                             "url_bnf"])
            for key in self.all_book_alignments.keys():
                book_alignment_output: BookAlignment = self.all_book_alignments[key]
                writer.writerow([key,
                                 book_alignment_output.key_used_to_align_bnf,
                                 book_alignment_output.similarity_ratio_bnf,
                                 book_alignment_output.isbn_constellation,
                                 book_alignment_output.isbn_bnf,
                                 book_alignment_output.age_range_constellation,
                                 book_alignment_output.age_range_bnf,
                                 book_alignment_output.url_constellation,
                                 book_alignment_output.url_bnf])
