from __future__ import absolute_import, division, print_function

import re

from imps.rebuilders import (
    does_line_end_in_noqa,
    Rebuilder
)

from imps.strings import get_doc_string

IMPORT_LINE = r'^import\s.*'
FROM_IMPORT_LINE = r'^from\s.*import\s.*'
FROM_IMPORT_LINE_WITH_PARAN = r'^from\s.*import\s.*\('


# We do sorting here early for a single line with multiple imports.
def sort_from_import(s):
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
        self.reader = ReadInput(indent)
        self.rebuilder = Rebuilder(type, max_line_length, local_imports, indent)

    def sort(self, lines):
        return self.rebuilder.rebuild(*self.reader.split_it(lines))


class ReadInput():
    def __init__(self, indent):
        self.indent = indent

    def clean(self):
        self.lines_before_import = []
        self.pre_import = {}
        self.pre_from_import = {}

    # I dont think this should be done here
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
            self.pre_from_import[sort_from_import(l)] = self.remove_double_newlines(self.lines_before_import)
            self.lines_before_import = []
        else:
            self.lines_before_import.append(l)

    # I don't like the fact we sort this block here.
    # but comments inside "from X import (Y #hi\n,Z)" are tricky
    def process_from_paran_block(self, l):

        if '#' not in l:
            # squash to normal
            l = l.replace('(', '').replace(')', '')
            self.pre_from_import[sort_from_import(l)] = self.remove_double_newlines(self.lines_before_import)
            self.lines_before_import = []
            return

        base = l[0:l.find('(') + 1]

        l = l[l.find('(') + 1:l.rfind(')')]
        pre_comments = []
        pre_imp_comment = {}
        same_line_comment = {}
        old_import = None
        while l:
            is_newline = l.find('\n') < l.find('#')

            l = l.lstrip()
            if l.find('#') != 0:
                end_marker = l.find(',')
                if end_marker == -1:
                    end_marker = l.find('#')
                if end_marker == -1:
                    end_marker = l.find('\n')

                old_import = l[0:end_marker]
                if not old_import:
                    break
                same_line_comment[old_import] = ''
                pre_imp_comment[old_import] = pre_comments
                pre_comments = []
                l = l[end_marker + 1:]
            else:
                comment = l[l.find('#'):l.find('\n')]

                if is_newline or not old_import:
                    pre_comments.append(comment)
                else:
                    same_line_comment[old_import] = comment
                    pre_imp_comment[old_import] = pre_comments
                    pre_comments = []
                l = l[l.find('\n'):]

        for i in sorted(same_line_comment.keys(), key=lambda s: s.lower()):
            if pre_imp_comment.get(i):
                for c in pre_imp_comment[i]:
                    base += '\n' + self.indent + c
            base += '\n' + self.indent + i + ','
            if same_line_comment[i]:
                base += " " + same_line_comment[i]

        # include the last pre import comments - they were at the end
        for c in pre_comments:
            base += '\n' + self.indent + c

        base += '\n)'
        self.pre_from_import[base] = self.lines_before_import
        self.lines_before_import = []

    def is_line_an_import(self, l):
        return re.match(FROM_IMPORT_LINE, l) or re.match(IMPORT_LINE, l)

    def split_it(self, text):
        self.clean()
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

            # If no doc_strings found (or doc string open and closed on same line):
            if len(doc_string_points) % 2 == 0:
                if re.match(FROM_IMPORT_LINE_WITH_PARAN, data):
                    while True:
                        i += 1
                        l = lines[i]
                        data += '\n' + l
                        if ')' in l and ('#' not in l or l.find(')') < l.find('#')):
                            break

                    self.process_from_paran_block(data)
                else:
                    self.process_line(data)
                data = ""
            else:
                giant_comment = doc_string_points[-1][1]

                while True:
                    i += 1
                    data += '\n'
                    comment_point = lines[i].find(giant_comment)
                    if comment_point != -1:
                        after_comment = lines[i][comment_point + 3:]
                        doc_string_points = get_doc_string(after_comment)

                        if len(doc_string_points) % 2 == 0:
                            data += lines[i]
                            self.process_line(data)
                            data = ""
                            break
                        else:
                            giant_comment = doc_string_points[-1][1]

                    else:
                        data += lines[i]
        return self.pre_import, self.pre_from_import, self.lines_before_import
