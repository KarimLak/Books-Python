def escape_quotes_in_file(file_path):
    with open(file_path, 'r') as f:
        content = f.readlines()

    new_content = []
    for line in content:
        new_line = line.replace('"', '\\"')
        new_content.append(new_line)

    with open(file_path, 'w') as f:
        for line in new_content:
            f.write(line)

escape_quotes_in_file('./new_awards.ttl')
