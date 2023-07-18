def fix_ttl_file(input_file, output_file):
    with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
        for line in f_in:
            line = line.rstrip()
            if "ns1:resume" in line:
                if line.endswith("' ;"):
                    line = line[:-3] + '" ;'
            f_out.write(line + '\n')

# usage
fix_ttl_file('your_file.ttl', 'fixed_file.ttl')
