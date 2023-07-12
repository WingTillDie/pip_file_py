#!/usr/bin/env python3
# Search the file is owned by what pip package
# similar to dpkg -S, pacman -Q, rpm -qo

# See also https://stackoverflow.com/questions/33483818/how-to-find-which-pip-package-owns-a-file#33484229

import re
import subprocess
import shlex
import sys

ESC = "\x1b"
CSI = f"{ESC}["

def SGR(num: int):
    return f'{CSI}{num}m'

intensity_increase = SGR(1)
intensity_reset = SGR(22)
fg_red = SGR(31)
fg_reset = SGR(39)

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

def usage():
    print('''Usage:\n ./pip-file.py <filename>''')

def is_has_files(lines, cur_index):
    return lines[cur_index+10] != 'Cannot locate RECORD or installed-files.txt'

if __name__ == '__main__':
    if len(sys.argv) != 2:
        # Wrong number of arguments
        usage()
        exit(1)
    elif sys.argv[1] == '-h' or sys.argv[1] == '--help':
        usage()
        exit()
    elif sys.argv[1][0] == '-':
        print("Unknown option: " + sys.argv[1], file=sys.stderr)
        usage()
        exit(1)
    
    # BETTER search via string or regex ?
    # finditer then highlight ?
    # BETTER case insensitive ?

    # TODO change to input
    #search_string = 'level'
    #search_string = 'AutoHotkey'

    search_string = sys.argv[1]

    bash_script = '''
    tmp=$(pip list)

    # Remove header
    tmp=$(<<< "$tmp" tail -n +3)
    # format: package version

    # Get packages (first field)
    tmp=$(<<< "$tmp" cut -d' ' -f1)

    # Query each package
    tmp=$(<<< "$tmp" xargs pip show -f)

    # Print result
    <<< "$tmp" cat
    '''

    # pip list | tail -n +3 | cut -d" " -f1 | xargs pip show -f | fgrep 'Files:' -B10
    # Name is -10, Location is -3

    #output = subprocess.check_output(bash_script, shell=True, executable='/usr/bin/bash')
    output = subprocess.check_output('pip list | tail -n +3 | cut -d" " -f1 | xargs pip show -f', shell=True)
    output = output.decode()
    lines = output.splitlines()

    def search_in_filenames(search_string, lines, cur_index, next_index):
        # TODO what is is the last ?
        if next_index is not None:
            files_range = (cur_index+10, next_index-1)
        else:
            files_range = (cur_index+10, None)
        files_lines = lines[slice(*files_range)]
        filenames = [line[2:] for line in files_lines]

        is_first_match = True
        for filename in filenames:
            try:
                match_index = filename.index(search_string)
            except ValueError as e:
                # search_string IS NOT found in current filename
                pass
            else:
                # search_string IS found in current filename
                #print(filename)
                if is_first_match:
                    # Name: 
                    print(lines[cur_index])
                    print(lines[cur_index+7])
                    is_first_match = False
                print('  ' + str_highlight(filename, match_index, match_index+len(search_string)))

    def str_indices(lines: list[str], object_to_search: str):
        return [i for i, n in enumerate(lines) if n == object_to_search]
    files_indices = str_indices(lines, 'Files:')
    names_indices = [index-10 for index in files_indices]

    iterator = reversed(names_indices)
    prev_item = None
    for item in iterator:
        cur_index, next_index = item, prev_item
        if is_has_files(lines, cur_index):
            search_in_filenames(search_string, lines, cur_index, next_index)
        prev_item = item


# TODO files index is +10:-1

# Speed is slow
if False:
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

    # TODO
    def search_string_in_package_files(search_string, package):
        output = subprocess.check_output(shlex.split(f'pip show -f {package}'))
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

        # BETTER all matches ?

        # Is this part (exception) slow ?
        is_first_match = True
        if False:
            for filename in filenames:
                if search_string in filename:
                    match_index = filename.index(search_string)
                    if is_first_match:
                        print('Name: ' + package_name)
                        print('Location: ' + package_location)
                        is_first_match = False
                    print('  ' + str_highlight(filename, match_index, match_index+len(search_string)))
        if True:
            for filename in filenames:
                try:
                    match_index = filename.index(search_string)
                except ValueError as e:
                    # search_string IS NOT found in current filename
                    pass
                else:
                    # search_string IS found in current filename
                    #print(filename)
                    if is_first_match:
                        print('Name: ' + package_name)
                        print('Location: ' + package_location)
                        is_first_match = False
                    print('  ' + str_highlight(filename, match_index, match_index+len(search_string)))
                    #print(str_unhighlight(str_highlight(filename, match_index, match_index+len(search_string))))

    for package in packages:
        search_string_in_package_files(search_string, package)
