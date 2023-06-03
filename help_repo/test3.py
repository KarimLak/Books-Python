from rdflib import Graph

g = Graph()
g.parse("./new_awards.ttl", format="turtle", encoding="utf-8")
g.parse("./1_awards_conversion_final_demo.ttl", format="turtle", encoding="utf-8")

qres = g.update("""
    PREFIX ns1: <http://schema.org/>
    PREFIX mcc: <http://example.com/mcc#> 
    PREFIX pbs: <http://example.com/pbs#>
    
    INSERT {
        ?award mcc:R37 ?book ;
               mcc:MCC-R35-4 ?year .
    }
    WHERE {
        ?book a ns1:Book ;
            ns1:award ?award ;
            ns1:dateReceived ?year .
        ?award a mcc:MCC-E12 .
        FILTER NOT EXISTS {?award mcc:R37 ?bookExisting .}
        FILTER NOT EXISTS {?award mcc:MCC-R35-4 ?yearExisting .}
    }
""")

# Write to output file
with open('output.ttl', 'w', encoding='utf-8') as f:
    for prefix, uri in g.namespaces():
        f.write(f'@prefix {prefix}: <{uri}> .\n')
    for s, p, o in g:
        f.write(f'<{s}> <{p}> <{o}> .\n')
