from __future__ import absolute_import, division, print_function

import re
from collections import OrderedDict

from enum import Enum

from imps.stdlib import FUTURE, get_paths, LOCAL, RELATIVE, STDLIB, THIRDPARTY

# Comments inside an import () currently get moved above it
from imps.strings import (
    get_doc_string,
    strip_to_module_name,
    strip_to_module_name_from_import
)


IMPORT_LINE = r'^import\s.*'
FROM_IMPORT_LINE = r'^from\s.*import\s.*'
FROM_IMPORT_LINE_WITH_PARAN = r'^from\s.*import\s.*\('
NOQA = r'.*\s*\#\sNOQA\s*$'  # wont work if NOQA is inside a triple string.


class Style(Enum):
    SMARKETS = 1
    GOOGLE = 2
    CRYPTOGRAPHY = 3


def get_style(s):
    if s in ('s', 'smarkets'):
        return Style.SMARKETS
    elif s in ('g', 'google'):
        return Style.GOOGLE
    elif s in ('c', 'crypto', 'cryptography'):
        return Style.CRYPTOGRAPHY
    else:
        raise Exception('Unknown style type %s', s)


def does_line_end_in_noqa(line):
    return re.match(NOQA, line)


def get_core_import(imp):
    imp = re.sub('^from\s+', '', imp)
    imp = re.sub('^import\s+', '', imp)
    return re.sub('\s+.*', '', imp)


def sorter(s):
    s = s.replace('.', chr(ord('z') + 1))
    return s.lower()


def sorter_unify_import_and_from(s):
    s = re.sub('^from\s+', '', s)
    s = re.sub('^import\s+', '', s)
    return sorter(s)


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
    def __init__(self, type='s', max_line_length=80, local_imports=None):
        self.type = get_style(type)
        self.max_line_length = max_line_length
        self.local_imports = local_imports or []

    def sort(self, lines):
        self.lines_before_import = []
        self.pre_import = {}
        self.pre_from_import = {}
        self.split_it(lines)
        return self.rebuild()

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
                        data += lines[i].strip()

    # -----------------rebuilders:-------------
    def rebuild(self):
        imports_by_type = classify_imports(self.pre_import.keys(), strip_to_module_name, self.local_imports)
        from_imports_by_type = classify_imports(
            self.pre_from_import.keys(), strip_to_module_name_from_import, self.local_imports
        )
        output = ""

        for type, imports in imports_by_type.items():
            self.first_import = True

            # try and inject these functions in instead.
            if self.type == Style.SMARKETS:
                for imp in sorted(imports, key=sorter):
                    output += self.build(imp, self.pre_import[imp])

                for imp in sorted(from_imports_by_type[type], key=sorter):
                    output += self.build(imp, self.pre_from_import[imp])

            if self.type == Style.GOOGLE:
                for imp in sorted(imports + from_imports_by_type[type], key=sorter_unify_import_and_from):
                    output += self.build(imp, self.pre_import.get(imp, self.pre_from_import.get(imp)))

            if self.type == Style.CRYPTOGRAPHY:
                # STDLIB is smarkets style
                if type in (STDLIB, FUTURE, RELATIVE):
                    for imp in sorted(imports, key=sorter):
                        output += self.build(imp, self.pre_import[imp])

                    for imp in sorted(from_imports_by_type[type], key=sorter):
                        output += self.build(imp, self.pre_from_import[imp])
                else:
                    last_imp = ''
                    for imp in sorted(imports + from_imports_by_type[type], key=sorter_unify_import_and_from):
                        if not last_imp or not get_core_import(imp).startswith(last_imp):
                            if last_imp:
                                if imp in self.pre_import:
                                    self.pre_import.get(imp).append('')
                                if imp in self.pre_from_import:
                                    self.pre_from_import.get(imp).append('')
                            last_imp = get_core_import(imp)

                        output += self.build(imp, self.pre_import.get(imp, self.pre_from_import.get(imp)))

        output = output[1:]
        return output + '\n'.join(self.lines_before_import)

    def build(self, imp, pre_imp):
        output = ""
        if self.first_import:
            found_double_newline = False
            for i in pre_imp:
                if i == '':  # TODO and not in giant_comment
                    found_double_newline = True
                    break
            if not found_double_newline:
                pre_imp.insert(0, '')

        if pre_imp:
            if not self.first_import:
                while len(pre_imp) > 1 and pre_imp[-1] == '' and pre_imp[-2] == '':
                    pre_imp = pre_imp[0:-1]
            output = '\n'.join(pre_imp) + '\n'

        if self.first_import:
            self.first_import = False

        output += imp + '\n'
        return output


def classify_imports(imports, strip_to_module, local_imports):
    result = OrderedDict()
    result[FUTURE] = []
    result[STDLIB] = []
    result[THIRDPARTY] = []
    result[LOCAL] = []
    result[RELATIVE] = []

    for i in imports:
        result[get_paths(strip_to_module(i), local_imports)].append(i)
    return result
