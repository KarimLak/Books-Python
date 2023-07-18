def fix_ttl_file(input_file, output_file):
    with open(input_file, 'r', encoding="utf-8") as f_in, open(output_file, 'w', encoding="utf-8") as f_out:
        for line in f_in:
            line = line.rstrip()
            if "ns1:genre" in line:
                line = line.replace("'", '"')
            f_out.write(line + '\n')

# usage
fix_ttl_file('output_bnf_1_updated.ttl', 'output_bnf_1_updated_1.ttl')
