from rdflib import Graph, Namespace, URIRef

# Create a namespace for schema
ns1 = Namespace("http://schema.org/")

# Path to the input file
input_file = "./1_final_output_merged_final_demo.ttl"

# Old URL to replace
old_url = "https://livresgg.ca/gagnants-et-finalistes-precedents"

# New URL to replace
new_url = "https://prixdeslibraires.qc.ca/"

# Create a new graph and load the book file into it
g = Graph()
g.parse(input_file, format="turtle")

# Iterate over all books
for s in g.subjects(None, ns1.Book):
    awards = [str(award) for award in g.objects(s, ns1.award)]
    urls = [str(url) for url in g.objects(s, ns1.url)]
    name = g.value(s, ns1.name)

    # Check if the award string contains 'Prix des libraires du Québec'
    if any('Prix des libraires du Québec' in award for award in awards):
        # Check if the book has multiple awards
        if len(awards) > 1:
            print(f"Book '{name}' has multiple awards.")
        # Only if old_url exists, replace it
        elif old_url in urls:
            # Remove the old url
            g.remove((s, ns1.url, URIRef(old_url)))
            # Add the new url
            g.add((s, ns1.url, URIRef(new_url)))

# Save the updated graph
g.serialize(destination='./1_final_output_merged_final_demo.ttl', format='turtle')
