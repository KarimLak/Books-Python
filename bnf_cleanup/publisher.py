def clean_publisher(line):
    if 'ns1:publisher' in line:
        if '"' in line:  # Ensure line can be split
            publisher_info = line.split('"')
            if ';' in publisher_info[1]:
                publisher_info[1] = publisher_info[1].split(';')[0].strip()
            cleaned_line = '"'.join(publisher_info)
            return cleaned_line
    return line

with open('output_bnf_updated.ttl', 'r', encoding='utf-8') as file:
    lines = file.readlines()

cleaned_lines = [clean_publisher(line) for line in lines]

with open('output_bnf_updated_clean.ttl', 'w', encoding='utf-8') as file:
    file.writelines(cleaned_lines)
