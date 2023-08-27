import requests
import pandas as pd
from urllib.parse import urlparse, parse_qs

def parse_bnf_url(url):
    """Parse BNF URL and return the ID."""
    parsed_url = urlparse(url)
    parsed_query = parse_qs(parsed_url.query)
    if 'id' in parsed_query:
        return parsed_query['id'][0]
    return None

export_file = 'export_public_2.csv'

# Create a new DataFrame to store the IDs.
df_ids = pd.DataFrame(columns=['ID'])

with open(export_file, 'r', encoding="utf-8") as f:
    lines = f.readlines()

for line in lines:
    try:
        # We expect the first item in the line to be the URL.
        url = line.split(';')[0].strip('"')
        bnf_id = parse_bnf_url(url)
        if bnf_id is not None:
            df_ids = df_ids.append({'ID': bnf_id}, ignore_index=True)
    except:
        # Ignore lines that cause an error.
        pass

# Print the DataFrame.
print(df_ids)
