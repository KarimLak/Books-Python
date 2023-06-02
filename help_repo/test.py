from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, SKOS, XSD, OWL
import os

g = Graph()

# Define namespaces
ns1 = Namespace("http://schema.org/")
pbs = Namespace("http://projetbs.org/")
xsd = Namespace("http://www.w3.org/2001/XMLSchema#")
mcc = Namespace("http://mcc.org/")
g.bind("ns1", ns1)
g.bind("pbs", pbs)
g.bind("xsd", xsd)
g.bind("mcc", mcc)

# Load your existing ttl file
g.parse("./1_awards_conversion_final_demo.ttl", format="turtle")

# Load your book ttl file
book_g = Graph()

book_g.parse("./1_final_output_merged_final_demo.ttl", format="turtle")

# Create new graph
new_g = Graph()

# Add ontology definitions only once
new_g.add((ns1.groupeAge, RDF.type, OWL.DatatypeProperty))
new_g.add((ns1.groupeAge, RDFS.domain, ns1.Award))
new_g.add((ns1.groupeAge, RDFS.range, XSD.integer))
new_g.add((ns1.groupeAge, RDFS.label, Literal("groupe d'âge")))

new_g.add((ns1.genreLitteraire, RDF.type, OWL.ObjectProperty))
new_g.add((ns1.genreLitteraire, RDFS.domain, ns1.Award))
new_g.add((ns1.genreLitteraire, RDFS.range, ns1.GenreLitteraire))
new_g.add((ns1.genreLitteraire, RDFS.label, Literal("genre littéraire associé à un prix")))

for award in g.subjects(RDF.type, ns1.Award):
    new_g.add((award, RDF.type, pbs.Award))

    for p, o in g.predicate_objects(subject=award):
        if str(p) == str(ns1.name):
            new_g.add((award, RDFS.label, o))
            new_g.add((award, ns1.description, Literal("An award for the science enquiry in the field of scientific policing")))

    for narrower_award in g.objects(subject=award, predicate=SKOS.narrower):
        new_g.add((narrower_award, RDF.type, pbs.Award))

        for p, o in g.predicate_objects(subject=narrower_award):
            if str(p) == str(ns1.name):
                new_g.add((narrower_award, RDFS.label, o))
            elif str(p) == str(ns1.to):
                for book in book_g.subjects(ns1.award, narrower_award):
                    new_g.add((URIRef(str(narrower_award) + str(o)), mcc.MCC_E12, book))
                    new_g.add((URIRef(str(narrower_award) + str(o)), ns1.award, narrower_award))
                    new_g.add((URIRef(str(narrower_award) + str(o)), mcc.MCC_R35_4, Literal(o, datatype=XSD.gYear)))
                    new_g.add((URIRef(str(narrower_award) + str(o)), mcc.R37, Literal("La science enquête les métiers de la police scientifique")))

        # Add the skos:narrower relationships separately after all properties have been added
        new_g.add((award, SKOS.narrower, narrower_award))

# Save your new graph to a ttl file
new_g.serialize(destination='new_awards.ttl', format='turtle')
