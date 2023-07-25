from rdflib import Graph, Namespace, URIRef

# create a namespace object for ns1
ns1 = Namespace("http://schema.org/")  # replace with your actual namespace URI

# initialize a graph
g = Graph()

try:
    # parse a file into the graph
    g.parse("./output_bnf_2.ttl", format="turtle")  # replace with your actual input file name
except Exception as e:
    print(f"An error occurred while parsing the file: {e}")

# remove all triples with the ns1:ageRange predicate
to_remove = [triple for triple in g.triples((None, ns1.ageRange, None))]
for triple in to_remove:
    g.remove(triple)

try:
    # save the modified graph to a new file
    g.serialize(destination='output.ttl', format='turtle')  # replace with your desired output file name
except Exception as e:
    print(f"An error occurred while writing the output file: {e}")
