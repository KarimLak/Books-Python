# open the source file
with open("output_bnf_2.ttl", "r", encoding="utf-8") as source:
    # open the destination file
    with open("output_bnf_2_updated.ttl", "w", encoding="utf-8") as destination:
        # iterate over each line in the source file
        for line in source:
            # check if the line contains 'ns1:resume' or 'ns1:noticeCritique'
            if 'ns1:resume' in line or 'ns1:noticeCritique' in line:
                # replace double quotes with single quotes inside the literal
                start_index = line.find('"')
                if start_index != -1:
                    end_index = line.rfind('"')
                    if end_index != -1 and end_index > start_index:
                        literal = line[start_index+1:end_index]
                        updated_literal = literal.replace('"', "'")
                        line = line[:start_index+1] + updated_literal + line[end_index:]
            # if the line contains 'ns1:resume', replace the last single quote with a double quote if not an empty string
            if 'ns1:resume' in line:
                last_single_quote = line.rfind("'")
                if last_single_quote != -1 and (line.find("'") != last_single_quote): # checking for empty string
                    line = line[:last_single_quote] + '"' + line[last_single_quote+1:]
                elif line.find("'") == last_single_quote:  # empty resume
                    line = line[:last_single_quote] + '"' + line[last_single_quote+1:]
            # add a newline before each semicolon that is followed by 'ns1:'
            line = line.replace(" ; ns1:", " ;\nns1:")
            # add four spaces before 'ns1:genre' and 'ns1:avisCritique'
            line = line.replace("\nns1:genre", "\n    ns1:genre")
            line = line.replace("\nns1:avisCritique", "\n    ns1:avisCritique")
            # write the updated line to the destination file
            destination.write(line)
