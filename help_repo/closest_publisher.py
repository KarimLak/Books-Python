from difflib import SequenceMatcher

# Function to find the best matching publisher
def best_matching_publisher(publisher, publisher_list):
    best_match = publisher
    best_ratio = 0

    for candidate in publisher_list:
        ratio = SequenceMatcher(None, publisher, candidate).ratio()
        if ratio > best_ratio:
            best_match = candidate
            best_ratio = ratio

    return best_match

def get_publishers_list(filepath):
    with open(filepath, 'r') as f:
        return [line.strip() for line in f.readlines()]

# Get the publishers list from the file
publishers_list = get_publishers_list('./publishers.csv')

# Your input string
input_string = "Edition"

# Find the closest publisher and print it
closest_publisher = best_matching_publisher(input_string, publishers_list)
print(f'Original Publisher: {input_string} | Closest Publisher: {closest_publisher}')
