class BookAlignment:
    def __init__(self, isbn_constellation=None, isbn_bnf=None, age_range_constellation=None,
                 age_range_bnf=None, url_constellation=None, url_bnf=None, url_lurelu=None, isbn_lurelu=None, uri_bnf=None, uri_constellation=None, uri_lurelu=None, name=None, author=None, date=None, publisher=None):
        self.similarity_ratio_lurelu = 0
        self.key_used_to_align_bnf = None
        self.key_used_to_align_lurelu = None
        self.uri_lurelu = uri_lurelu

        self.isbn_constellation = isbn_constellation
        self.age_range_constellation = age_range_constellation
        self.url_constellation = url_constellation
        self.uri_constellation = uri_constellation

        self.isbn_bnf = isbn_bnf
        self.age_range_bnf = age_range_bnf
        self.url_bnf = url_bnf
        self.uri_bnf = uri_bnf

        self.url_lurelu = url_lurelu
        self.isbn_lurelu = isbn_lurelu

        self.name = name
        self.author = author
        self.publisher = publisher
        self.date = date


    def align_bnf(self, key_used_to_align_bnf=None, isbn_bnf=None, url_bnf=None, uri_bnf=None, similarity_ratio_bnf=None, age_range_bnf=None):
        self.key_used_to_align_bnf = key_used_to_align_bnf
        self.isbn_bnf = isbn_bnf
        self.url_bnf = url_bnf
        self.uri_bnf = uri_bnf
        self.similarity_ratio_bnf = similarity_ratio_bnf
        self.age_range_bnf = age_range_bnf

    def align_lurelu(self,  isbn_lurelu=None,  url_lurelu=None, similarity_ratio_lurelu=None, key_used_to_align_lurelu=None, uri_lurelu=None):
        self.similarity_ratio_lurelu = similarity_ratio_lurelu
        self.key_used_to_align_lurelu = key_used_to_align_lurelu
        self.url_lurelu = url_lurelu
        self.isbn_lurelu = isbn_lurelu
        self.uri_lurelu = uri_lurelu