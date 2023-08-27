import re

with open('output_bnf_2.ttl', 'r', encoding="utf-8") as infile, open('output_bnf_final.ttl', 'w', encoding="utf-8") as outfile:
    for line in infile:
        if line.startswith('    ns1:author'):
            # Extract the author's name.
            author = re.findall(r'"(.*?)"', line)[0]
            # Remove the unwanted part enclosed within brackets.
            author_no_brackets = re.sub(r'\(.*?\)', '', author)
            # Split on comma, and remove the unwanted parts after dot
            author_parts = [name.strip() for name in author_no_brackets.split(',')]
            if len(author_parts) > 1:
                author_parts[1] = author_parts[1].split('.')[0]
                # Only join with space if there is a secondary part.
                author_transformed = ' '.join(reversed(author_parts)).strip()
            else:
                author_transformed = author_parts[0]
            # Remove any extra white space from author_transformed.
            author_transformed = re.sub(' +', ' ', author_transformed)
            # Replace the author's name in the line.
            line = line.replace(author, author_transformed)
        outfile.write(line)
