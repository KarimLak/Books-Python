import re

with open('output_bnf_2.ttl', 'r', encoding="utf-8") as infile, open('output_bnf_final.ttl', 'w', encoding="utf-8") as outfile:
    for line in infile:
        if line.startswith('    ns1:title'):
            # Extract the title.
            title = re.findall(r'"(.*?)"', line)[0]
            # If title contains '/', keep only what comes before it.
            if '/' in title:
                title = title.split('/')[0]
            # If title contains '(', keep only what comes before it.
            if '(' in title:
                title = title.split('(')[0]
            # Strip any leading or trailing whitespace.
            title = title.strip()
            # Replace the title in the line.
            line = re.sub(r'\".*?\"', f'"{title}"', line)
        outfile.write(line)
