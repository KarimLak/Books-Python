from googlesearch import search

# the name of the book you are searching for
book_name = "To Kill a Mockingbird"

# the query you want to search
query = book_name + " Babelio"

# use the search function from the googlesearch library to perform the search
for j in search(query, num_results=1):
    print(j)
