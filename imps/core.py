from __future__ import absolute_import, division, print_function

import re
from collections import OrderedDict

from enum import Enum

from stdlib import FUTURE, get_paths, LOCAL, RELATIVE, STDLIB, THIRDPARTY
from strings import get_doc_string, strip_to_module_name, strip_to_module_name_from_import


IMPORT_LINE = r'^import\s.*'
FROM_IMPORT_LINE = r'^from\s.*import\s.*'


class Style(Enum):
    SMARKETS = 1
    GOOGLE = 2
    CRYPTOGRAPHY = 3


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


def split_from_import(s):
    from_part, import_list = re.split('\s+import\s+', s)
    imps = import_list.split(',')
    imps = sorted(set([i.strip() for i in imps]), key=lambda s: s.lower())
    return from_part + " import " + ', '.join(imps)


class Sorter():
    def __init__(self, type):
        self.type = type

    def sort(self, lines):
        self.lines_before_import = []
        self.pre_import = {}
        self.pre_from_import = {}

        self.split_it(lines)
        return self.rebuild()

    def process_line(self, l):
        if re.match(IMPORT_LINE, l):
            self.pre_import[l] = self.lines_before_import
            self.lines_before_import = []
        elif re.match(FROM_IMPORT_LINE, l):
            self.pre_from_import[split_from_import(l)] = self.lines_before_import
            self.lines_before_import = []
        else:
            self.lines_before_import.append(l)

    def split_it(self, text):
        myl = ''
        giant_comment = False

        for l in text.split('\n'):
            myl += l.rstrip() + '\n'

            doc_string_points = get_doc_string(l, 0, in_doc_string=giant_comment)

            if len(doc_string_points) % 2 == 0:
                if not giant_comment:
                    self.process_line(myl.rstrip())
                    myl = ''
            else:
                if giant_comment:
                    myl += "\n" + l[0:doc_string_points[0]]
                    self.process_line(myl.rstrip())
                    rest = l[doc_string_points[0] + 3:].rstrip()
                    if rest:
                        self.process_line(rest)
                    myl = ''

                giant_comment = not giant_comment

    # -----------------rebuilders:-------------
    def rebuild(self):
        imports_by_type = classify_imports(self.pre_import.keys(), strip_to_module_name)
        from_imports_by_type = classify_imports(self.pre_from_import.keys(), strip_to_module_name_from_import)
        output = ""

        for type, imports in imports_by_type.items():
            self.first_import = True

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


def classify_imports(imports, strip_to_module):
    result = OrderedDict()
    result[FUTURE] = []
    result[STDLIB] = []
    result[THIRDPARTY] = []
    result[LOCAL] = []
    result[RELATIVE] = []

    for i in imports:
        result[get_paths(strip_to_module(i))].append(i)
    return result
