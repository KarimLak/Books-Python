import re

with open('output_bnf_2.ttl', 'r', encoding="utf-8") as infile, open('output_bnf_final.ttl', 'w', encoding="utf-8") as outfile:
    for line in infile:
        if line.startswith('    ns1:language'):
            # Extract the language.
            language = re.findall(r'"(.*?)"', line)[0]
            # If language contains 'français', keep only 'français'.
            if 'français' in language:
                language = 'français'
            # Replace the language in the line.
            line = re.sub(r'\".*?\"', f'"{language}"', line)
        outfile.write(line)
