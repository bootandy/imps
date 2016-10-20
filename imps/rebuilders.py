from __future__ import absolute_import, division, print_function

import re
from collections import OrderedDict

from imps.stdlib import FUTURE, get_paths, LOCAL, RELATIVE, STDLIB, THIRDPARTY

from imps.strings import strip_to_module_name, strip_to_module_name_from_import


NOQA = r'.*\s*\#\sNOQA\s*$'  # wont work if NOQA is inside a triple string.
FROM_IMPORT_LINE = r'^from\s.*import\s.*'


def does_line_end_in_noqa(line):
    return re.match(NOQA, line)


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


def get_core_import(imp):
    imp = re.sub('^from\s+', '', imp)
    imp = re.sub('^import\s+', '', imp)
    return re.sub('\s+.*', '', imp)


def sorter(s):
    s = s.replace('.', chr(ord('z') + 1))
    # We only alphabetically sort the from part of the imports in style: from X import Y
    if re.match(FROM_IMPORT_LINE, s):
        return s[0:s.find(' import ')].lower() + s[s.find(' import '):]
    return s.lower()


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


def smarkets_builder(imports, from_imports, type, pre_import, pre_from_import, build):
    output = ""
    for imp in sorted(imports, key=sorter):
        output += build(imp, pre_import[imp])

    for imp in sorted(from_imports[type], key=sorter):
        output += build(imp, pre_from_import[imp])
    return output


def google_builder(imports, from_imports, type, pre_import, pre_from_import, build):
    output = ""
    for imp in sorted(imports + from_imports[type], key=sorter_unify_import_and_from):
        output += build(imp, pre_import.get(imp, pre_from_import.get(imp)))
    return output


def crypto_builder(imports, from_imports, type, pre_import, pre_from_import, build):
    output = ""
    if type in (STDLIB, FUTURE, RELATIVE):
        for imp in sorted(imports, key=sorter):
            output += build(imp, pre_import[imp])

        for imp in sorted(from_imports[type], key=sorter):
            output += build(imp, pre_from_import[imp])
    else:
        last_imp = ''
        for imp in sorted(imports + from_imports[type], key=sorter_unify_import_and_from):
            if not last_imp or not get_core_import(imp).startswith(last_imp):
                if last_imp:
                    if imp in pre_import:
                        pre_import.get(imp).append('')
                    if imp in pre_from_import:
                        pre_from_import.get(imp).append('')
                last_imp = get_core_import(imp)

            output += build(imp, pre_import.get(imp, pre_from_import.get(imp)))
    return output


class Rebuilder():
    def __init__(self, type='s', max_line_length=80, local_imports=None, indent="    "):
        self.builder_func = get_builder_func(type)
        self.max_line_length = int(max_line_length)
        self.local_imports = local_imports or []
        self.indent = indent

    def rebuild(self, pre_import, pre_from_import, remaining_lines):
        imports_by_type = classify_imports(pre_import.keys(), strip_to_module_name, self.local_imports)
        from_imports_by_type = classify_imports(
            pre_from_import.keys(), strip_to_module_name_from_import, self.local_imports
        )
        output = ""

        for type, imports in imports_by_type.items():
            self.first_import = True
            output += self.builder_func(
                imports, from_imports_by_type, type, pre_import, pre_from_import, self.build
            )

        output = output[1:]
        return output + '\n'.join(remaining_lines)

    #  Can we make this a func not a method
    def build(self, core_import, pre_imp):
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

        output += self.split_core_import(core_import) + '\n'
        return output

    def split_core_import(self, core_import):
        if len(core_import) <= self.max_line_length or does_line_end_in_noqa(core_import):
            return core_import

        result = (',\n' + self.indent).join([s.strip() for s in core_import.split(',')])
        result = re.sub(r'import\s+', 'import (\n' + self.indent, result)
        result += "\n)"
        return result
