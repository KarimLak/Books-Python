import re

def clean_up(input_file: str, output_file: str):
    in_resume = False
    in_notice_critique = False
    multiline_string = ''
    indentation = ''

    with open(input_file, 'r', encoding='utf-8') as infile, \
            open(output_file, 'w', encoding='utf-8') as outfile:

        lines = infile.readlines()
        for i in range(len(lines)):
            line = lines[i]
            stripped_line = line.strip()

            if stripped_line.startswith('ns1:resume'):
                in_resume = True
                attribute = 'ns1:resume'
                multiline_string = stripped_line
                indentation = re.match(r'\s*', line).group()
            elif stripped_line.startswith('ns1:noticeCritique'):
                in_notice_critique = True
                attribute = 'ns1:noticeCritique'
                multiline_string = stripped_line
                indentation = re.match(r'\s*', line).group()
            elif stripped_line.endswith('" ;') and (in_resume or in_notice_critique):
                in_resume = False
                in_notice_critique = False
                multiline_string += " " + stripped_line
                outfile.write(indentation + re.sub(r'\s+', ' ', multiline_string.lstrip()) + '\n')
                multiline_string = ''
                indentation = ''
                attribute = ''
            elif in_resume or in_notice_critique:
                if i+1 < len(lines) and lines[i+1].strip().startswith('ns1:Book'):
                    outfile.write(indentation + re.sub(r'\s+', ' ', multiline_string.lstrip()) + '\n\n')
                    multiline_string = ''
                    in_resume = False
                    in_notice_critique = False
                    continue
                multiline_string += " " + stripped_line
            else:
                outfile.write(line)

        if multiline_string:
            outfile.write(indentation + re.sub(r'\s+', ' ', multiline_string.lstrip()) + '\n')

if __name__ == '__main__':
    clean_up('output_bnf_2.ttl', 'output_bnf_h.ttl')
