import re

with open('output_bnf_2.ttl', 'r', encoding="utf-8") as infile, open('output_bnf_final.ttl', 'w', encoding="utf-8") as outfile:
    for line in infile:
        if line.startswith('    ns1:publisher'):
            # Extract the publisher's name.
            publisher = re.findall(r'"(.*?)"', line)[0]
            # Remove the unwanted part enclosed within brackets.
            publisher_no_brackets = re.sub(r'\(.*?\)', '', publisher)
            # Strip any leading or trailing whitespace.
            publisher_transformed = publisher_no_brackets.strip()
            # Replace the publisher's name in the line.
            line = line.replace(publisher, publisher_transformed)
        outfile.write(line)
