# open the source file
with open("output_bnf_2.ttl", "r", encoding="utf-8") as source:
    # open the destination file
    with open("output_bnf_1_updated.ttl", "w", encoding="utf-8") as destination:
        # iterate over each line in the source file
        for line in source:
            # check if the line contains 'ns1:author'
            if 'ns1:title' in line:
                # find the last double quote
                end_index = line.rfind('"')
                if end_index != -1:
                    # if there is a double quote just before the last double quote, remove it
                    if line[end_index-1] == '"':
                        line = line[:end_index-1] + line[end_index:]
            # write the updated line to the destination file
            destination.write(line)
