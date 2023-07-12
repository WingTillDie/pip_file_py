#!/usr/bin/env python3
# Search the file is owned by what pip package
# similar to dpkg -S, pacman -Q, rpm -qo

import re
import subprocess
import shlex

bash_script = '''
tmp=$(pip list)

# Remove header
tmp=$(<<< "$tmp" tail -n +3)
# format: package version

# Get packages (first field)
tmp=$(<<< "$tmp" cut -d' ' -f1)

# Print result
<<< "$tmp" cat
'''

output = subprocess.check_output(bash_script, shell=True, executable='/usr/bin/bash')
output = output.decode()
packages = output.splitlines()

# BETTER search via string or re ?
# BETTER case insensitive ?

# BETTER change to input
search_string = 'level'

# TODO
def search_string_in_package_files(search_string, package):
    pass

for package in packages:
    search_string_in_package_files(search_string, package)



output = subprocess.check_output(shlex.split('pip show -f ahk-binary'))
output = output.decode()

# Input can be pip show -f ahk-binary
#def get_files(output: str):
lines = output.splitlines()

prefix = 'Name: '
for line in lines:
    if line[:len(prefix)] == prefix:
        package_name = line[len(prefix):]
        break

prefix = 'Location: '
for line in lines:
    if line[:len(prefix)] == prefix:
        package_location = line[len(prefix):]
        break

files_line_index = lines.index('Files:')
files_lines = lines[files_line_index+1:]

# Relative path of files
filenames = [line[2:] for line in files_lines]

# '\n'.join(lines[line_index+1:])



# BETTER highlight hit
# BETTER disable color
filenames[6].index('level')

# BETTER all matches ?

ESC = "\x1b"
CSI = f"{ESC}["

def SGR(num: int):
    return f'{CSI}{num}m'

intensity_increase = SGR(1)
intensity_reset = SGR(22)
fg_red = SGR(31)
fg_reset = SGR(39)

# TODO not tested
def str_insert(self: str, index: int, object: str):
    # Similar to list.insert for str
    return self[:index] + object + self[index:]

def str_highlight(filename: str, start_index, end_index):
    highlight = f'{intensity_increase}{fg_red}'
    unhighlight = f'{intensity_reset}{fg_reset}'
    
    # Insert at end_index then insert at start_index for correct position to insert
    filename = str_insert(filename, end_index, unhighlight)
    filename = str_insert(filename, start_index, highlight)
    return filename

def str_unhighlight(filename_highlighted: str):
    # Substitute SGR with ''
    #pattern = '%s\d{1,3}(;\d{1,3})*m' % re.escape(CSI)
    from string import Template
    pattern = Template('${CSI}\d{1,3}(;\d{1,3})*m').substitute(CSI=re.escape(CSI))
    filename = re.sub(pattern, '', filename_highlighted)
    return filename

for filename in filenames:
    try:
        match_index = filename.index('level')
    except ValueError as e:
        # search_string IS NOT found in current filename
        pass
    else:
        # search_string IS found in current filename
        #print(filename)
        print('Name: ' + package_name)
        print('Location: ' + package_location)
        print('  ' + str_highlight(filename, match_index, match_index+len(search_string)))
        #print(str_unhighlight(str_highlight(filename, match_index, match_index+len(search_string))))