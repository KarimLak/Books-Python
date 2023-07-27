from rdflib import Graph, Namespace, URIRef

# create a namespace object for ns1
ns1 = Namespace("http://schema.org/")  # replace with your actual namespace URI

# initialize a graph
g = Graph()

# parse a file into the graph
g.parse("./output_bnf_updated.ttl", format="turtle")  # replace with your actual input file name

# build a dictionary to store unique ns1:bnfLink attributes
bnf_links = {}

# iterate through the graph
for s, p, o in g.triples((None, ns1.bnfLink, None)):
    # if the ns1:bnfLink attribute is not in the dictionary, add it
    if str(o) not in bnf_links:
        bnf_links[str(o)] = s
    else:
        # remove the book with duplicate ns1:bnfLink attribute
        to_remove = [triple for triple in g.triples((s, None, None))]
        for triple in to_remove:
            g.remove(triple)

# save the modified graph to a new file
g.serialize(destination='output_bnf_no_duplicates.ttl', format='turtle')  # replace with your desired output file name
