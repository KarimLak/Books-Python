def modify_ttl(file_path):
    with open(file_path, 'r') as f:
        content = f.readlines()

    new_content = []
    for i, line in enumerate(content):
        # If line is not empty
        if line.strip():
            # Check if we're not at the last line before trying to access i+1
            if i+1 < len(content) and content[i+1].strip() == '':
                new_line = line.rstrip()  # Remove trailing spaces
                new_line = new_line[:-1] + ".\n"  # Replace last character with "."
            else:
                new_line = line.rstrip()  # Remove trailing spaces
                new_line = new_line[:-1] + ";\n"  # Replace last character with ";"
            new_content.append(new_line)
        else:
            new_content.append(line)

    with open(file_path, 'w') as f:
        for line in new_content:
            f.write(line)

modify_ttl('./new_awards.ttl')
