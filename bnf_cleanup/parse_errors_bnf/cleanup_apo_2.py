def fix_ttl_file(input_file, output_file):
    with open(input_file, 'r', encoding="utf-8") as f_in, open(output_file, 'w', encoding="utf-8") as f_out:
        for line in f_in:
            line = line.rstrip()
            if "ns1:resume" in line:
                if line.endswith("' ;"):
                    line = line[:-3] + '" ;'
            f_out.write(line + '\n')

# usage
fix_ttl_file('output_bnf_2.ttl', 'fixed_file.ttl')
