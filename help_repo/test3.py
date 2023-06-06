import uuid
import re

def replace_ids(input_file_path, output_file_path):
    # Read the input file
    with open(input_file_path, 'r') as file:
        lines = file.readlines()

    # Open the output file
    with open(output_file_path, 'w') as file:
        # Initialize new_id to None. This will hold the new UUID for each book.
        new_id = None
        for line in lines:
            # If we encounter a line that starts a book description, generate a new UUID
            if line.strip().endswith("a ns1:Book ;"):
                new_id = uuid.uuid4()
                line = re.sub(r"(ns1:Book[a-zA-Z0-9_-]+)", f"ns1:Book{new_id}", line)
            # If we encounter any other line that contains a book ID, replace it with the current UUID
            elif re.search(r"ns1:Book[a-zA-Z0-9_-]+", line):
                line = re.sub(r"(ns1:Book[a-zA-Z0-9_-]+)", f"ns1:Book{new_id}", line)
            # Write the line to the output file
            file.write(line)

# Replace ids in your file
replace_ids('./missing_output_3.ttl', './missing_output_3.ttl')
