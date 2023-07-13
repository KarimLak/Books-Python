import re

input_file_path = "output_constellation.ttl"
output_file_path = "output_constellation.ttl"

with open(input_file_path, 'r', encoding="utf-8") as file:
    data = file.read()

# find all occurrences of 'pbs:keyword "<keyword>" ;' and replace with 'pbs:keyword "<keyword>",'
data = re.sub(r'(pbs:keyword ".*?") ;', r'\1,', data)

# write the corrected data to the output file
with open(output_file_path, 'w',encoding="utf-8") as file:
    file.write(data)
