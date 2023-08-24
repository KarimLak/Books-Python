def extract_info(notice):
    if "- Le " not in notice:
        return notice, None, None, None
    
    # Extract date
    start_index = notice.find("- Le ") + 5
    date_str = notice[start_index:start_index + 8]
    formatted_date = "{}-{}-{}".format(date_str[:4], date_str[4:6], date_str[6:])

    # Extract author
    start_author = notice.find(", par ") + 6
    if " (publié dans" in notice:
        end_author = notice.find(" (publié dans")
    elif "(" in notice:
        end_author = notice.find("(")
    else:
        end_author = notice.find('" ;', start_author)
    author_name = notice[start_author:end_author].strip()

    # Extract source
    start_source = notice.find("(publié dans ") + 13
    if ")" in notice[start_source:]:
        end_source = notice.find(")", start_source)
        source = notice[start_source:end_source].strip()
    else:
        source = notice[start_source:].strip()

    # Remove extra info from noticeCritique
    modified_notice = notice[:notice.find("- Le ")].strip()

    return modified_notice, formatted_date, author_name, source

with open('output_bnf.ttl', 'r', encoding="utf-8") as f:
    lines = f.readlines()

modified_lines = []

i = 0
while i < len(lines):
    line = lines[i]
    if 'pbs:noticeCritique' in line:
        notice = line[line.find('"')+1:line.rfind('"')]
        modified_notice, date, author, source = extract_info(notice)

        line = line.replace(notice, modified_notice)
        modified_lines.append(line)

        if date:
            modified_lines.append(f'    pbs:avisDate "{date}" ;\n')
        if author:
            modified_lines.append(f'    pbs:avisAuthor "{author}" ;\n')
        if source:
            modified_lines.append(f'    pbs:avisSource "{source}" ;\n')
    else:
        modified_lines.append(line)
    i += 1

with open('output_bnf_transformed.ttl', 'w', encoding="utf-8") as f:
    f.writelines(modified_lines)

print("Transformation complete. Check 'output_bnf_transformed.ttl' for results.")
