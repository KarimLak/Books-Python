def read_file(file_name):
    with open(file_name, 'r', encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]

def extract_publishers_from_ttl(file_name):
    # This is a simple extraction based on a presumption that publishers appear in a specific pattern in the TTL file.
    # If the TTL structure is more complex, you might need a more sophisticated parsing mechanism.
    publishers = set()
    with open(file_name, 'r', encoding="utf-8") as f:
        for line in f:
            if 'publisher' in line:  # assuming a line containing 'publisher' holds the publisher info
                # This extracts a string between double quotes. This might need to be adjusted based on the actual format.
                publisher = line.split('"')[1] if '"' in line else None
                if publisher:
                    publishers.add(publisher.strip())
    return publishers

# Load publishers from both files
known_publishers = set(read_file('publishers.txt'))
ttl_publishers = extract_publishers_from_ttl('output_bnf.ttl')

# Find publishers in the known list that are not in the ttl and remove them
to_keep = [publisher for publisher in known_publishers if publisher in ttl_publishers]

# Write the filtered publishers back to publishers.txt
with open('publishers.txt', 'w', encoding="utf-8") as f:
    for publisher in to_keep:
        f.write(publisher + '\n')
