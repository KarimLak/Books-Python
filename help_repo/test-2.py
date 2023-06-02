from rdflib import Graph, Namespace

g = Graph()
g.parse("1_awards_conversion_final_demo.ttl", format="turtle")  # Replace 'file.rdf' with your RDF file

n1 = Namespace("http://schema.org/")  # Replace with your namespace
g.bind('ns1', n1)

qres = g.query(
    """
    PREFIX ns1: <http://schema.org/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

    CONSTRUCT {
        ?parentAward skos:narrower ?childAward .
    }
    WHERE {
        ?parentAward ns1:subOrganization ?childAward .
    }
    """)

# create a new graph and add the results of the query to it
result_graph = Graph()

# Bind namespace prefixes to the result graph
result_graph.bind('ns1', n1)
result_graph.bind('skos', 'http://www.w3.org/2004/02/skos/core#')

result_graph += qres

# serialize the graph to a file
result_graph.serialize(destination='result.ttl', format='turtle')
