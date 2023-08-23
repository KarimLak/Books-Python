import re

def replace_quotes(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()

    def replacement(match):
        return match.group(1) + match.group(2).replace('"', "'") + match.group(3)

    # Find the content inside ns1:reviewBody and replace double quotes with single quotes
    content = re.sub(r'(ns1:reviewBody ")(.*?)"( .;)', replacement, content, flags=re.DOTALL)

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

filename = 'output_books.ttl'
replace_quotes(filename)
print("Double quotes inside ns1:reviewBody have been replaced with single quotes.")
