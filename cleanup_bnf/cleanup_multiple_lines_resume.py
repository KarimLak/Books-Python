import re

def clean_up(input_file: str, output_file: str):
    in_resume = False
    resume_line = ''
    indentation = ''

    with open(input_file, 'r', encoding='utf-8') as infile, \
            open(output_file, 'w', encoding='utf-8') as outfile:

        for line in infile:
            stripped_line = line.strip()
            if stripped_line.startswith('ns1:resume'):
                in_resume = True
                resume_line = stripped_line
                indentation = re.match(r'\s*', line).group()
            elif stripped_line.endswith('" ;') and in_resume:
                in_resume = False
                resume_line += " " + stripped_line
                outfile.write(indentation + re.sub(r'\s+', ' ', resume_line.lstrip()) + '\n')
                resume_line = ''
                indentation = ''
            elif in_resume:
                resume_line += " " + stripped_line
            else:
                outfile.write(line)

        if in_resume:
            outfile.write(indentation + re.sub(r'\s+', ' ', resume_line.lstrip()) + '\n')

if __name__ == '__main__':
    clean_up('output_bnf_2.ttl', 'output_bnf_h.ttl')
