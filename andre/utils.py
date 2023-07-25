def create_key(book_name, book_author=None, publisher=None, publication_date=None):
    if book_name and not book_author and not publisher and not publication_date:
        return book_name

    if book_name and book_author and not publisher and not publication_date:
        return book_name + "_" + book_author

    if book_name and book_author and publisher and not publication_date:
        return book_name + "_" + book_author + "_" + publisher

    if book_name and book_author and publisher and publication_date:
        return book_name + "_" + book_author + "_" + publisher + "_" + publication_date
