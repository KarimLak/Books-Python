def create_award_file(input_file_path, output_file_path):
    with open(input_file_path, 'r') as f:
        content = f.readlines()

    awards = []
    for line in content:
        if line.strip().endswith('mcc:MCC-E12 ;'):
            award = line.strip().split(' ')[0] + ',\n'
            awards.append(award)

    with open(output_file_path, 'w') as f:
        f.writelines(awards)


create_award_file('./updated_award_blocks.ttl', './awards_list.txt')
