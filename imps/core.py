from __future__ import absolute_import, division, print_function

import re

from imps.rebuilders import does_line_end_in_noqa, Rebuilder

# Comments inside an import () currently get moved above it
from imps.strings import get_doc_string

IMPORT_LINE = r'^import\s.*'
FROM_IMPORT_LINE = r'^from\s.*import\s.*'
FROM_IMPORT_LINE_WITH_PARAN = r'^from\s.*import\s.*\('


# We do sorting here early for a single line with multiple imports.
def split_from_import(s):
    from_part, import_list = re.split('\s+import\s+', s)
    imps = import_list.split(',')
    imps = sorted(set([i.strip() for i in imps if i.strip()]), key=lambda s: s.lower())
    return from_part + " import " + ', '.join(imps)


def split_imports(s):
    _, import_list = re.split('^import\s+', s)
    imps = import_list.split(',')
    imps = sorted(set([i.strip() for i in imps if i.strip()]), key=lambda s: s.lower())
    return "import " + ', '.join(imps)


class Sorter():
    def __init__(self, type='s', max_line_length=80, local_imports=None, indent="    "):
        self.reader = ReadInput()
        self.rebuilder = Rebuilder(type, max_line_length, local_imports, indent)

    def sort(self, lines):
        return self.rebuilder.rebuild(*self.reader.split_it(lines))


class ReadInput():
    def __init__(self):
        self.lines_before_import = []
        self.pre_import = {}
        self.pre_from_import = {}

    def remove_double_newlines(self, lines):
        i = 0
        while i < len(lines) - 1:
            if lines[i+1] == lines[i] == '':
                lines[i:i+1] = []
            else:
                i += 1
        return lines

    def process_line(self, l):
        if does_line_end_in_noqa(l):
            self.lines_before_import.append(l)
        elif re.match(IMPORT_LINE, l):
            self.pre_import[split_imports(l)] = self.remove_double_newlines(self.lines_before_import)
            self.lines_before_import = []
        elif re.match(FROM_IMPORT_LINE, l):
            self.pre_from_import[split_from_import(l)] = self.remove_double_newlines(self.lines_before_import)
            self.lines_before_import = []
        else:
            self.lines_before_import.append(l)

    def is_line_an_import(self, l):
        return re.match(FROM_IMPORT_LINE, l) or re.match(IMPORT_LINE, l)

    def split_it(self, text):
        lines = text.split('\n')
        data = ''
        i = -1
        while i < len(lines) - 1:
            i += 1
            data += lines[i]

            if '\\' in data and data.strip()[-1] == '\\' and self.is_line_an_import(lines[i]):
                data = data.strip()[0:-1]
                continue

            doc_string_points = get_doc_string(data)

            if len(doc_string_points) % 2 == 0:
                if re.match(FROM_IMPORT_LINE_WITH_PARAN, data):
                    while True:
                        i += 1
                        l = lines[i]
                        if '#' in l:
                            pre_hash, post_hash = l[0:l.find('#')], l[l.find('#'):]
                            self.lines_before_import.append(post_hash)
                            l = pre_hash

                        data += l.strip()
                        if ')' in l:
                            data = data.replace('(', '')
                            data = data.replace(')', '')
                            break

                self.process_line(data)
                data = ""
            else:
                giant_comment = doc_string_points[-1][1]

                while True:
                    i += 1
                    data += '\n'
                    comment_point = lines[i].find(giant_comment)
                    if comment_point != -1:
                        data += lines[i][0:comment_point + 3]
                        self.process_line(data)

                        # Doesnt work if we start a triple comment here again.
                        data = lines[i][comment_point + 3:]
                        if data:
                            # want to: GOTO start of this loop
                            self.process_line(data)
                        break
                    else:
                        data += lines[i]
        return self.pre_import, self.pre_from_import, self.lines_before_import
