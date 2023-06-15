from collections import defaultdict

def print_duplicate_uri_books(ttl_filename):
    # Create a dictionary to store book URIs and their count
    uri_dict = defaultdict(int)

    # Open and read the ttl file line by line
    with open(ttl_filename, 'r', encoding='utf-8') as file:
        for line in file:
            # Ignore lines without a "a" predicate which signifies rdf:type
            if ' a ' not in line:
                continue

            # The URI is the subject of the line, before the ' a ' predicate
            uri = line.split(' a ')[0].strip()
            uri_dict[uri] += 1

    # Print the URIs that have multiple occurrences
    for uri, count in uri_dict.items():
        if count > 1:
            print(f"URI {uri} appears {count} times")

# Call the function with your ttl file name
print_duplicate_uri_books("./awards.ttl")