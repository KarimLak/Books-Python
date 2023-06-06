import re
from difflib import SequenceMatcher

def best_matching_publisher(publisher, publisher_dict):
    best_match = publisher
    best_ratio = 0

    for candidate, ns_format in publisher_dict.items():
        ratio = SequenceMatcher(None, publisher.lower(), candidate.lower()).ratio()
        if ratio > best_ratio:
            best_match = ns_format
            best_ratio = ratio

    return best_match

# Load publishers from the conversion file
publishers = {}
with open('1_publishers_conversion_demo.ttl', 'r', encoding="utf-8") as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        match_name = re.search(r'ns1:name "(.*?)"', line)
        match_publisher = re.search(r'ns1:(.*?) a ns1:Publisher', lines[i-1])
        if match_name and match_publisher:
            publishers[match_name.group(1)] = match_publisher.group(1)

# Load books and replace publishers
with open('./missing_output_1.ttl', 'r', encoding="utf-8") as f:
    data = f.readlines()

new_data = []
for line in data:
    match = re.search(r'ns1:publisher "(.*?)"', line)
    if match:
        publisher = match.group(1)
        best_match = best_matching_publisher(publisher, publishers)
        new_line = line.replace(f'"{publisher}"', f'ns1:{best_match}')
        new_data.append(new_line)
    else:
        new_data.append(line)

# Write output to a new file
with open('missing_output_1.ttl', 'w', encoding="utf-8") as f:
    f.writelines(new_data)
