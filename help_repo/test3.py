import re

# 1. Build a mapping of award IDs to dates from 1_awards_conversion_final_demo.ttl
award_to_date_map = {}

with open('./1_awards_conversion_final_demo.ttl', 'r', encoding="utf-8") as file:
    content = file.read()
    blocks = content.split('\n\n')

    for block in blocks:
        award_match = re.search(r'ns1:(\S+) a ns1:Award', block)
        if award_match:
            award_id = award_match.group(1).strip()
            date_match = re.search(r'ns1:date "(\S+)"', block)
            if date_match:
                date = date_match.group(1).strip()
                award_to_date_map[award_id] = date

# 2. Update the new_awards.ttl file, adding the appropriate date triples
with open('./new_awards.ttl', 'r', encoding="utf-8") as file:
    content = file.read()

new_content = ""
blocks = content.split('\n\n')

for block in blocks:
    award_match = re.search(r'ns1:(\S+) a mcc:MCC-E12', block)
    if award_match:
        award_id = award_match.group(1).strip()
        if award_id in award_to_date_map:
            date = award_to_date_map[award_id]
            # Check if there are less than three attributes
            attributes = block.split('\n')
            if len(attributes) <= 3:
                block = block.rstrip() + f'\n    mcc:MCC-R35-4 "{date}"^^xsd:gYear .'
    new_content += block + "\n\n"

with open('./new_awards.ttl', 'w', encoding="utf-8") as file:
    file.write(new_content.strip())
