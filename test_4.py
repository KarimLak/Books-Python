import csv

def read_csv_file(file_path):
    with open(file_path, 'r', encoding= "utf-8") as f:
        reader = csv.reader(f)
        data_list = list(reader)
    
    # Flattens the list if it's a list of lists
    data_list = [item for sublist in data_list for item in sublist]

    return data_list

def write_to_file(file_path, data):
    with open(file_path, 'w', encoding= "utf-8") as f:
        f.write("[")
        for item in data[:-1]:
            f.write('"' + item + '",')
        f.write('"' + data[-1] + '"')
        f.write("]")

file_path = './query_result.txt'
names = read_csv_file(file_path)

# Removing duplicates and sorting the list
unique_names = sorted(list(set(names)))

# Writing to a new file
write_to_file('./query_result.txt', unique_names)
