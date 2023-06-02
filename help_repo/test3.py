from rdflib import Graph, Namespace, URIRef
import re
import urllib.parse

# Namespaces
ns1 = Namespace("http://schema.org/")
mcc = Namespace("http://example.org/mcc/")

# Load the awards graph
awards_g = Graph()
awards_g.parse("./1_awards_conversion_final_demo.ttl", format="turtle", encoding="utf-8")

# Function to find parent award URI
def find_parent_award(award_uri):
    parent_award = None
    # Decode URL before finding parent
    decoded_award_uri = urllib.parse.unquote(award_uri)
    for s, p, o in awards_g.triples((None, ns1.subOrganization, URIRef(decoded_award_uri))):
        parent_award = s
        break
    return parent_award

def process_line(line):
    match = re.match(r'(ns1:\S+) a mcc:MCC-E12 ;', line, re.DOTALL)
    if match:
        uri_str = match.group(1)
        # Strip "ns1:" prefix
        uri_str = uri_str[4:]
        # Handle special characters
        uri_str = urllib.parse.quote(uri_str, safe='')
        award_uri = URIRef(f'http://schema.org/{uri_str}')
        print(f'Award URI: {award_uri}')

        # Find parent award
        parent_award_uri = find_parent_award(str(award_uri))
        print(f'Parent Award URI: {parent_award_uri}')
        if parent_award_uri is not None:
            parent_award_ref = parent_award_uri.split('/')[-1]
            line = line.strip() + f'\n    ns1:award :{parent_award_ref} ;\n'
    return line

def process_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with open(output_file, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(process_line(line))

process_file('./new_awards.ttl', './new_awards.ttl')
