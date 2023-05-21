import csv

def title_case_name(name):
    words = name.split()
    title_cased_words = [word[0].upper() + word[1:] for word in words]
    return " ".join(title_cased_words)

seen = {}  # Keep track of lines we've seen before

# Open the CSV file with utf-8 encoding
with open('./query-result-publishers.csv', 'r', encoding='utf-8') as file:
    csv_reader = csv.reader(file)

    # Create new rows but with the name in title case and without duplicates
    for row in csv_reader:
        name = row[0]  # Get the first column
        title_cased_name = title_case_name(name)
        # Create a canonical form of the name
        canonical_name = " ".join(sorted(set(title_cased_name.split())))
        if canonical_name not in seen or len(title_cased_name) > len(seen[canonical_name]):
            seen[canonical_name] = title_cased_name

# Convert the seen dictionary to a list of rows
new_rows = [[name] for name in seen.values()]

# Sort the rows in alphabetical order
new_rows.sort()

# Write the changes to a new CSV file with utf-8 encoding
with open('query-result-publishers_modified.csv', 'w', newline='', encoding='utf-8') as file:
    csv_writer = csv.writer(file)
    csv_writer.writerows(new_rows)  # write the new rows
