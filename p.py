import re

def read_publishers_from_ttl(file_name):
    with open(file_name, 'r', encoding="utf-8") as f:
        content = f.read()

    # Extract publisher details
    publishers = re.findall(r'ns1:(\w+) a ns1:Publisher ;\n\s+ns1:name "(.*?)"', content)
    return {name: ttl_name for ttl_name, name in publishers}

def replace_publishers_in_output_bnf(publishers):
    with open('output_bnf.ttl', 'r', encoding="utf-8") as f:
        content = f.read()

    # Replace publishers
    for publisher_name, ttl_name in publishers.items():
        content = content.replace(f'ns1:publisher "{publisher_name}"', f'ns1:publisher ns1:{ttl_name}')

    # Write back the updated content
    with open('output_bnf.ttl', 'w', encoding="utf-8") as f:
        f.write(content)

publishers = read_publishers_from_ttl('publishers.ttl')
replace_publishers_in_output_bnf(publishers)
