# Open the input file
with open("output_bnf_2.ttl", "r", encoding="utf-8") as infile:
    lines = infile.readlines()

# Determine the midpoint of the file
mid = len(lines) // 2

# Write the first half of the lines to the first output file
with open("output_first_half.ttl", "w", encoding="utf-8") as outfile1:
    outfile1.writelines(lines[:mid])

# Write the second half of the lines to the second output file
with open("output_second_half.ttl", "w", encoding="utf-8") as outfile2:
    outfile2.writelines(lines[mid:])
