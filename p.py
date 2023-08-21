import re

def filter_isbn(filename):
    # This pattern checks for exactly 13 digits in a string.
    pattern = re.compile(r'^\d{13}$')

    with open(filename, 'r') as file:
        lines = file.readlines()

    # Filter lines that match the pattern
    valid_lines = [line for line in lines if pattern.match(line.strip())]

    # Write the valid ISBNs back to the file
    with open(filename, 'w') as file:
        file.writelines(valid_lines)

filter_isbn('isbn.txt')
