def add_url_attribute(file_path, output_file_path, url_string):
    with open(file_path, 'r') as f:
        content = f.readlines()

    new_content = []
    current_block = []
    for line in content:
        current_block.append(line)
        if line.strip().endswith('.'):
            # Process the block
            if not any('ns1:url' in l for l in current_block):
                # Add the URL attribute if not present
                current_block.insert(-1, f'    ns1:url "{url_string}"^^xsd:string ;\n')
            new_content.extend(current_block)
            current_block = []

    with open(output_file_path, 'w') as f:
        for line in new_content:
            f.write(line)


url_string = "https://livresgg.ca/gagnants-et-finalistes-precedents"
add_url_attribute('./missing_output_1.ttl', './missing_output_1.ttl', url_string)
