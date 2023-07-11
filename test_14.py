def modify_illustrator(input_file_path, output_file_path):
    with open(input_file_path, 'r', encoding="utf-8") as input_file:
        lines = input_file.readlines()

    with open(output_file_path, 'w', encoding="utf-8") as output_file:
        for line in lines:
            if line.startswith('    ns1:illustrator'):
                # Split the illustrators if 'et' is in the line
                if ' et ' in line:
                    parts = line.split(' et ')
                    # Strip the illustrators and format them correctly
                    parts = [part.strip().replace('"', '') for part in parts]
                    line = '    ns1:illustrator "' + parts[0].strip() + '"^^xsd:string,\n' + '        "' + parts[1].strip() + '"^^xsd:string ;\n'
            output_file.write(line)

input_file_path = './output_constellation.ttl'
output_file_path = './output_constellation.ttl'

modify_illustrator(input_file_path, output_file_path)
