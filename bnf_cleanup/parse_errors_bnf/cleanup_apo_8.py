# open the source file
with open("output_bnf_2.ttl", "r", encoding="utf-8") as source:
    # open the destination file
    with open("output_bnf_1_updated.ttl", "w", encoding="utf-8") as destination:
        # iterate over each line in the source file
        for line in source:
            # check if the line contains 'ns1:description'
            if 'ns1:author' in line:
                # replace internal double quotes with single quotes inside the literal
                start_index = line.find('"')
                if start_index != -1:
                    end_index = line.rfind('"')
                    if end_index != -1 and end_index > start_index:
                        literal = line[start_index+1:end_index]
                        updated_literal = literal.replace('"', "'")
                        line = line[:start_index+1] + updated_literal + line[end_index:]
            # write the updated line to the destination file
            destination.write(line)
