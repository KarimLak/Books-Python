import random

seen_uris = set()

with open('output_bnf_updated.ttl', 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open('output_bnf_updated_unique.ttl', 'w', encoding='utf-8') as f:
    for line in lines:
        if line.startswith('ns1:Book'):
            uri = line.split()[0]
            while uri in seen_uris:
                uri = f"ns1:Book{random.randint(10000000,99999999)}"
            seen_uris.add(uri)
            line = line.replace(line.split()[0], uri)
        f.write(line)
