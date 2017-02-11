from __future__ import absolute_import, division, print_function

import re
from collections import OrderedDict

from imps.stdlib import FUTURE, get_paths, LOCAL, RELATIVE, STDLIB, THIRDPARTY


NOQA = r'.*\s*\#\sNOQA\s*$'  # wont work if NOQA is inside a triple string.
FROM_IMPORT_LINE = r'^from\s.*import\s.*'
FROM_IMPORT_PARAN_LINE = r'^from\s.*import\s\(.*'


def sortable_key(s):
    s = s.strip()
    broken_s = s.split(' ')
    results = []
    for bs in broken_s:
        new_s = ''
        for c in bs:
            if c.islower():
                new_s += '1'
            else:
                new_s += '0'
        results.append(bs.lower() + new_s)
    return ' '.join(results)


def does_line_end_in_noqa(line):
    return re.match(NOQA, line, re.IGNORECASE)


def classify_imports(imports, local_imports):
    result = OrderedDict()
    result[FUTURE] = []
    result[STDLIB] = []
    result[THIRDPARTY] = []
    result[LOCAL] = []
    result[RELATIVE] = []

    for i in imports:
        result[get_paths(i, local_imports)].append(i)

    return result


def get_core_import(imp):
    imp = re.sub('^from\s+', '', imp)
    imp = re.sub('^import\s+', '', imp)
    return re.sub('\s+.*', '', imp)


def sorter_relative_imports(s):
    s = s.replace('.', chr(ord('z') + 1))
    s = s.replace('_', chr(ord('A') - 1))
    return s.lower()


def sorter(s):
    s = s.replace('.', chr(ord('A') - 2))
    s = s.replace('_', chr(ord('A') - 1))
    # We only alphabetically sort the from part of the imports in style: from X import Y
    if re.match(FROM_IMPORT_PARAN_LINE, s):
        s = re.sub('\#.*\n', '', s)
        s = re.sub('\s+', ' ', s)
        s = sortable_key(s[4:s.find(' import ')]) + ' import' + s[s.find('(') + 1:s.find(')')]
    if re.match(FROM_IMPORT_LINE, s):
        s = sortable_key(s[4:s.find(' import ')]) + s[s.find(' import '):]
    return sortable_key(s)


def sorter_unify_import_and_from(s):
    s = re.sub('^from\s+', '', s)
    s = re.sub('^import\s+', '', s)
    return sorter(s)


def get_builder_func(s):
    if s in ('s', 'smarkets'):
        return smarkets_builder
    elif s in ('g', 'google'):
        return google_builder
    elif s in ('c', 'crypto', 'cryptography'):
        return crypto_builder
    else:
        raise Exception('Unknown style type %s', s)


def relative_builder_func(from_imports, pre_from_import, build):
    output = ""
    for imp in sorted(from_imports[RELATIVE], key=sorter_relative_imports):
        output += build(imp, pre_from_import[imp])
    return output


def smarkets_builder(imports, from_imports, type, pre_import, pre_from_import, build):
    output = ""
    for imp in sorted(imports[type], key=sorter):
        output += build(imp, pre_import[imp])

    for imp in sorted(from_imports[type], key=sorter):
        output += build(imp, pre_from_import[imp])
    return output


def google_builder(imports, from_imports, type, pre_import, pre_from_import, build):
    output = ""
    for imp in sorted(imports[type] + from_imports[type], key=sorter_unify_import_and_from):
        output += build(imp, pre_import.get(imp, pre_from_import.get(imp)))
    return output


def crypto_builder(imports, from_imports, type, pre_import, pre_from_import, build):
    output = ""
    if type in (STDLIB, FUTURE, RELATIVE):
        for imp in sorted(imports[type], key=sorter):
            output += build(imp, pre_import[imp])

        for imp in sorted(from_imports[type], key=sorter):
            output += build(imp, pre_from_import[imp])
    else:
        last_imp = ''
        for imp in sorted(imports[type] + from_imports[type], key=sorter_unify_import_and_from):
            if not last_imp or not get_core_import(imp).startswith(last_imp):
                if last_imp:
                    if imp in pre_import:
                        pre_import.get(imp).append('')
                    if imp in pre_from_import:
                        pre_from_import.get(imp).append('')
                last_imp = get_core_import(imp)

            output += build(imp, pre_import.get(imp, pre_from_import.get(imp)))
    return output


def remove_double_newlines(lines):
    i = 0
    while i < len(lines) - 1:
        if lines[i+1] == lines[i] == '':
            lines[i:i+1] = []
        else:
            i += 1
    return lines


class Rebuilder():
    def __init__(self, type='s', max_line_length=80, local_imports=None, indent="    "):
        self.builder_func = get_builder_func(type)
        self.max_line_length = int(max_line_length)
        self.local_imports = local_imports or []
        self.indent = indent

    def rebuild(self, pre_import, pre_from_import, lines_before_any_imports, remaining_lines):
        imports_by_type = classify_imports(pre_import.keys(), self.local_imports)
        from_imports_by_type = classify_imports(pre_from_import.keys(), self.local_imports)

        output = '\n'.join(lines_before_any_imports + [''])
        self.new_import_group = False

        types = imports_by_type.keys()
        types.remove(RELATIVE)

        for type in types:
            new_import_group = self.builder_func(
                imports_by_type, from_imports_by_type, type, pre_import, pre_from_import, self._build
            )
            if new_import_group:
                self.new_import_group = True
            output += new_import_group

        output += relative_builder_func(from_imports_by_type, pre_from_import, self._build)

        output = output.lstrip()
        return output + '\n'.join(remaining_lines)

    #  Can we make this a func not a method
    def _build(self, core_import, pre_imp):
        output = ""
        if not self.new_import_group:
            pre_imp = remove_double_newlines(pre_imp)
        else:  # ensure there is a new line
            if '' not in pre_imp:
                pre_imp.insert(0, '')

        self.new_import_group = False

        output += '\n'.join(pre_imp + [''])

        output += self._split_core_import(core_import) + '\n'
        return output

    def _split_core_import(self, core_import):
        if len(core_import) <= self.max_line_length or does_line_end_in_noqa(core_import) or (
                '(' in core_import and ')' in core_import):
            return core_import

        # To turn a long line of imports into a multiline import using parenthesis
        result = (',\n' + self.indent).join([s.strip() for s in core_import.split(',')])
        result = re.sub(r'import\s+', 'import (\n' + self.indent, result)
        result += ",\n)"
        return result
