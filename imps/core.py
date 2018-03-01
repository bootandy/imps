from __future__ import absolute_import, division, print_function

import re

from imps.rebuilders import does_line_end_in_noqa, Rebuilder, sortable_key
from imps.strings import get_doc_string


IMPORT_LINE = r'^import\s.*'
FROM_IMPORT_LINE = r'^from\s.*import\s.*'
FROM_IMPORT_LINE_WITH_PARAN = r'^from\s.*import\s.*\('


# We do sorting here early for a single line with multiple imports.
def sort_from_import(s):
    from_part, import_list = re.split('\s+import\s+', s, 1)
    imps = import_list.split(',')
    imps = sorted(set([i.strip() for i in imps if i.strip()]), key=sortable_key)
    return from_part + " import " + ', '.join(imps)


def split_imports(s):
    _, import_list = re.split('^import\s+', s, 1)
    imps = import_list.split(',')
    imps = sorted(set([i.strip() for i in imps if i.strip()]), key=sortable_key)
    return "import " + ', '.join(imps)


def is_line_an_import(l):
    return re.match(FROM_IMPORT_LINE, l) or re.match(IMPORT_LINE, l)


def _is_there_no_close_paran(l):
    return ')' not in l or ('#' in l and l.find('#') < l.find(')'))


class Sorter():
    def __init__(self, type='s', max_line_length=80, local_imports=None, indent="    "):
        self.reader = ReadInput(indent)
        self.rebuilder = Rebuilder(type, max_line_length, local_imports, indent)

    def sort(self, lines):
        self.reader.clean()
        self.reader.process_and_split(lines)
        return self.rebuilder.rebuild(*self.reader.get_imports_as_dicts())


class ReadInput():
    def __init__(self, indent):
        self.indent = indent

    def clean(self):
        self.lines_before_any_imports = None
        self.lines_before_import = []
        self.pre_import = {}
        self.pre_from_import = {}

    def _store_line(self, target_map, line):
        # Special case keep the first comments at the very top of the file (eg utf encodings)
        if self.lines_before_any_imports is None:
            self.lines_before_any_imports = self.lines_before_import
            self.lines_before_import = []
        target_map[line] = self.lines_before_import
        self.lines_before_import = []

    def _process_line(self, l):
        if does_line_end_in_noqa(l):
            self.lines_before_import.append(l)
        elif re.match(IMPORT_LINE, l):
            self._store_line(self.pre_import, split_imports(l))
        elif re.match(FROM_IMPORT_LINE_WITH_PARAN, l):
            self._process_from_paren_block(l)
        elif re.match(FROM_IMPORT_LINE, l):
            self._store_line(self.pre_from_import, sort_from_import(l))
        else:
            self.lines_before_import.append(l)

    def _process_from_paren_block(self, line):
        """
        If there are no comments we squash a from X import (Y,Z) into -> from X import Y,Z
        by removing the parenthesis

        However if there are comments we must split them into comments for the import on the line below
        the comment and comments on the same line as the import.

        Imports are then sorted inside this method to preserve the position of the comments.
        """

        if '#' not in line:
            line = line.replace('(', '').replace(')', '')
            self._store_line(self.pre_from_import, sort_from_import(line))
            return

        base = line[0:line.find('(') + 1]

        line = line[line.find('(') + 1:line.rfind(')')]
        pre_comments = []
        pre_imp_comment = {}
        same_line_comment = {}
        old_import = None
        while line:
            is_newline = line.find('\n') < line.find('#')

            line = line.lstrip()
            # If the next part of l is NOT a comment.
            if line.find('#') != 0:

                # l[0:end_marker] is the name of the next import
                end_marker = line.find(',')
                if end_marker == -1:
                    end_marker = line.find('#')
                if end_marker == -1:
                    end_marker = line.find('\n')

                old_import = line[0:end_marker]
                if not old_import:
                    break
                same_line_comment[old_import] = ''
                pre_imp_comment[old_import] = pre_comments
                pre_comments = []
                line = line[end_marker + 1:]
            else:
                comment = line[line.find('#'):line.find('\n')]

                # If the comment is on a newline mark it as a 'pre-import-comment' to go on the line above.
                # (or if old_import is None which means this is the first line).
                if is_newline or not old_import:
                    pre_comments.append(comment)
                else:
                    same_line_comment[old_import] = comment
                    if old_import not in pre_imp_comment:
                        pre_imp_comment[old_import] = []
                line = line[line.find('\n'):]

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

    def process_and_split(self, text):
        lines = text.split('\n')
        i = -1
        while i < len(lines) - 1:
            i += 1
            data = lines[i]

            if is_line_an_import(lines[i]) and '\\' in lines[i] and lines[i].strip()[-1] == '\\':
                while '\\' in lines[i] and lines[i].strip()[-1] == '\\' and i < len(lines) - 1:
                    data = data.strip()[0:-1] + lines[i+1]
                    i += 1

            if re.match(FROM_IMPORT_LINE_WITH_PARAN, data):
                while _is_there_no_close_paran(lines[i]) and i < len(lines) - 1:
                    i += 1
                    data += '\n' + lines[i]

            # If a doc_strings was opened but not closed on this line:
            doc_string_points = get_doc_string(data)
            if len(doc_string_points) % 2 == 1:
                giant_comment = doc_string_points[-1][1]

                while i < len(lines) - 1:
                    i += 1
                    data += '\n' + lines[i]
                    comment_point = lines[i].find(giant_comment)
                    if comment_point != -1:
                        after_comment = lines[i][comment_point + 3:]
                        doc_string_points = get_doc_string(after_comment)

                        if len(doc_string_points) % 2 == 0:
                            break
            self._process_line(data)

    def get_imports_as_dicts(self):
        if self.lines_before_any_imports is None:
            self.lines_before_any_imports = []
        return self.pre_import, self.pre_from_import, self.lines_before_any_imports, self.lines_before_import
