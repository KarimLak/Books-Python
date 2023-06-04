import re
import collections

award_to_books_map = collections.defaultdict(set)
existing_awards = collections.defaultdict(set)

# Parse awards from the 1_final_output_merged_final_demo.ttl file
with open('./1_final_output_merged_final_demo.ttl', 'r', encoding = "utf-8") as file:
    content = file.read()
    blocks = content.split('\n\n')  # Split blocks more accurately 

    for block in blocks:
        book_match = re.search(r'ns1:(Book\S+) a ns1:Book', block)
        if book_match:
            book_id = book_match.group(1)
            award_matches = re.findall(r'ns1:award ns1:(\S+)', block)
            for award_match in award_matches:
                award_id = award_match
                award_to_books_map[award_id].add(book_id)  

# Identify awards that already have a book assigned in the new_awards.ttl file
with open('./new_awards.ttl', 'r', encoding = "utf-8") as file:
    content = file.read()
    blocks = content.split('\n\n')  # Split blocks more accurately

    for block in blocks:
        award_match = re.search(r'ns1:(\S+) a mcc:MCC-E12', block)
        if award_match:
            award_id = award_match.group(1)
            book_match = re.search(r'mcc:R37 ns1:(Book\S+)', block)
            if book_match:
                existing_awards[award_id].add(book_match.group(1))

# Write to the new_awards.ttl file
new_content = ""
for block in blocks:
    new_content += block
    award_match = re.search(r'ns1:(\S+) a mcc:MCC-E12', block)
    if award_match:
        award_id = award_match.group(1)
        if award_id in award_to_books_map:
            for book_id in award_to_books_map[award_id]:
                if book_id not in existing_awards[award_id]:
                    new_content += f'\n    mcc:R37 ns1:{book_id} ;'
    new_content += '\n\n'  # Recreate the block separator

with open('./new_awards.ttl', 'w', encoding = "utf-8") as file:
    file.write(new_content.strip())  # Remove trailing newlines
