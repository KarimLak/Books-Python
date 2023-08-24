from rdflib import Graph, Namespace
import csv

# Define the namespace
ns1 = Namespace("http://schema.org/")

def extract_publishers_and_awards_to_csv(ttl_filepath, existing_publishers_csv_filepath, existing_awards_csv_filepath, new_publishers_csv_filepath, new_awards_csv_filepath):
    # Parse the ttl files 
    g = Graph()
    g.parse(ttl_filepath, format="turtle")

    # Get all books from the graph
    books = list(g.subjects(predicate=ns1["author"]))

    # Read existing publishers and awards from the existing csv files
    with open(existing_publishers_csv_filepath, 'r', encoding='utf-8') as f:
        existing_publishers = {line.replace("\n", "").strip().lower() for line in f}
    with open(existing_awards_csv_filepath, 'r', encoding='utf-8') as f:
        existing_awards = {line.replace("\n", "").strip().lower() for line in f}

    # Create sets to hold unique publishers and awards
    publishers = set()
    awards = set()

    for book in books:
        # Get publisher and award of the book
        publisher = g.value(subject=book, predicate=ns1["publisher"])
        award = g.value(subject=book, predicate=ns1["award"])

        # Add publisher and award to their respective sets
        if publisher is not None:
            publishers.add(str(publisher).strip().lower())
        if award is not None:
            awards.add(str(award).strip().lower())

    # Remove existing publishers and awards from the new ones
    publishers = sorted([publisher.title() for publisher in publishers if publisher not in existing_publishers])
    awards = sorted([award.title() for award in awards if award not in existing_awards])

    # Write new publishers to CSV
    with open(new_publishers_csv_filepath, "w", newline="", encoding='utf-8') as f:
        writer = csv.writer(f)
        for publisher in publishers:
            writer.writerow([publisher])

    # Write new awards to CSV
    with open(new_awards_csv_filepath, "w", newline="", encoding='utf-8') as f:
        writer = csv.writer(f)
        for award in awards:
            writer.writerow([award])

# Call the function with your ttl file name and output csv file names
extract_publishers_and_awards_to_csv("./output-ricochet-tables-2.ttl", "./query-result-publishers_modified.csv", "./query-result-awards.csv", "./publishers.csv", "./awards.csv")
