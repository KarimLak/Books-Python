import re

def replace_triple_quotes(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()

    # This function replaces the outer triple quotes with double quotes and removes inner triple quotes at the end
    def replacement(match):
        return 'ns1:text "' + match.group(1).replace('""" ;', '" ;').replace('\n', ' ') + '" ;'

    # Regular expression pattern to match the reviewBody content surrounded by triple quotes
    content = re.sub(r'ns1:text """(.*?)""" ;', replacement, content, flags=re.DOTALL)

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

filename = 'output_books.ttl'
replace_triple_quotes(filename)
print("Triple quotes in review bodies have been replaced.")
