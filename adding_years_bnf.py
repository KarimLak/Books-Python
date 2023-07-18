from rdflib import Graph, Namespace, Literal, URIRef

g = Graph()
g.parse("output_bnf_1.ttl", format="turtle")

# Define the namespace
ns1 = Namespace("http://schema.org/")

# Binding namespace to the graph
g.bind('schema', ns1)

# Mapping of publicDestinataire to ageRange
age_ranges = {
    "Adolescents - À partir de 13 ans": ['13', '14', '15', '16', '17'],
    "Bons lecteurs - À partir de 9 ans": ['9', '10', '11', '12'],
    "Bons lecteurs - À partir de 10 ans": ['10', '11', '12'],
    "Apprentissage - À partir de 3 ans": ['3', '4', '5'],
    "Lecteurs débutants - À partir de 6 ans": ['6', '7', '8'],
    "Bons lecteurs - À partir de 12 ans": ['12'],
    "Bons lecteurs - À partir de 11 ans": ['11', '12'],
    "Éveil - À partir de 1 an": ['1', '2', '3'],
    "Lecteurs débutants - À partir de 8 ans": ['8'],
    "Éveil - À partir de 2 ans": ['2', '3'],
    "Apprentissage - À partir de 4 ans": ['4', '5'],
    "Apprentissage - À partir de 5 ans": ['5'],
    "Lecteurs débutants - À partir de 7 ans": ['7', '8'],
    "Adolescents - À partir de 14 ans": ['14', '15', '16', '17'],
    "Adolescents - À partir de 15 ans": ['15', '16', '17']
}

for s, p, o in g.triples((None, ns1['publicDestinataire'], None)):
    if str(o) in age_ranges:
        for age in age_ranges[str(o)]:
            g.add((s, ns1['ageRange'], Literal(age)))

# Serialize the graph to Turtle format
g.serialize("output.ttl", format="turtle")
