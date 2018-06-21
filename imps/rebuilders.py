from __future__ import absolute_import, division, print_function

import re
from collections import OrderedDict

from imps.stdlib import FUTURE, get_paths, LOCAL, RELATIVE, STDLIB, THIRDPARTY


NOQA = r'.*\s*\#\sNOQA'  # wont work if NOQA is inside a triple string.
PYLINT_IGNORE = r'.*\s*\#\s*pylint:\s*disable\=.*$'  # wont work if pylint: disable is inside a triple string.

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


def does_line_have_hash_noqa(line):
    return re.match(NOQA, line, re.IGNORECASE)


def does_line_end_in_pylint_ignore(line):
    if re.match(PYLINT_IGNORE, line, re.IGNORECASE):
        _, post = re.split(r'#\spylint', line, re.IGNORECASE)
        if 'F0401' in post or 'E0611' in post:
            return True
    return False


def _classify_imports(imports, local_imports):
    result = OrderedDict()
    result[FUTURE] = []
    result[STDLIB] = []
    result[THIRDPARTY] = []
    result[LOCAL] = []
    result[RELATIVE] = []

    for i in imports:
        result[get_paths(i, local_imports)].append(i)

    return result


def _get_core_import(imp):
    imp = re.sub(r'^from\s+', '', imp)
    imp = re.sub(r'^import\s+', '', imp)
    return re.sub(r'\s+.*', '', imp)


def _sorter_relative_imports(s):
    s = s.replace('.', chr(ord('z') + 1))
    s = s.replace('_', chr(ord('A') - 1))
    return s.lower()


def _sorter(s):
    s = s.replace('.', chr(ord('A') - 2))
    s = s.replace('_', chr(ord('A') - 1))
    # We only alphabetically sort the from part of the imports in style: from X import Y
    if re.match(FROM_IMPORT_PARAN_LINE, s):
        s = re.sub(r'\#.*\n', '', s)
        s = re.sub(r'\s+', ' ', s)
        s = sortable_key(s[4:s.find(' import ')]) + ' import' + s[s.find('(') + 1:s.find(')')]
    if re.match(FROM_IMPORT_LINE, s):
        s = sortable_key(s[4:s.find(' import ')]) + s[s.find(' import '):]
    return sortable_key(s)


def _sorter_unify_import_and_from(s):
    s = re.sub(r'^from\s+', '', s)
    s = re.sub(r'^import\s+', '', s)
    return _sorter(s)


def _remove_double_newlines(lines):
    i = 0
    while i < len(lines) - 1:
        if lines[i+1] == lines[i] == '':
            lines[i:i+1] = []
        else:
            i += 1
    return lines


def _get_builder_func(s, max_line_length, indent):
    if s in ('s', 'smarkets'):
        return SmarketsBuilder(max_line_length, indent)
    elif s in ('g', 'google'):
        return GoogleBuilder(max_line_length, indent)
    elif s in ('c', 'crypto', 'cryptography'):
        return CryptoBuilder(max_line_length, indent)
    else:
        raise Exception('Unknown style type %s', s)


class GenericBuilder(object):
    def __init__(self, max_line_length, indent):
        self.max_line_length = max_line_length
        self.indent = indent

    def do_all(
            self, imports_by_type, from_imports_by_type, lines_before_any_imports, pre_import,
            pre_from_import, after_imports
    ):
        output = '\n'.join(lines_before_any_imports)
        self.new_import_group = False

        for typ in imports_by_type.keys():
            if typ == RELATIVE:
                continue
            new_import_group = self.special_sort(
                imports_by_type, from_imports_by_type, typ, pre_import, pre_from_import
            )
            if new_import_group:
                self.new_import_group = True
                output += new_import_group + '\n'

        output += self._relative_builder_func(from_imports_by_type, pre_from_import)
        output = output.strip()
        after_imports_str = '\n'.join(after_imports).strip()

        result = (output + '\n\n\n' + after_imports_str).strip()

        if result:
            return result + '\n'
        return ''

    def _relative_builder_func(self, from_imports, pre_from_import):
        output = ""
        for imp in sorted(from_imports[RELATIVE], key=_sorter_relative_imports):
            output += self._build(imp, pre_from_import[imp])
        return output

    def _build(self, core_import, pre_imp):
        pre_imp = [a for a in pre_imp if a]
        output = '\n'.join([''] + pre_imp + [''])
        output += self._split_core_import(core_import)
        return output

    def _split_core_import(self, core_import):
        if len(core_import) <= self.max_line_length or does_line_have_hash_noqa(core_import) or (
                '(' in core_import and ')' in core_import) or does_line_end_in_pylint_ignore(core_import):
            return core_import

        # To turn a long line of imports into a multiline import using parenthesis
        result = (',\n' + self.indent).join([s.strip() for s in core_import.split(',')])
        result = re.sub(r'import\s+', 'import (\n' + self.indent, result)
        result += ",\n)"
        return result

    def special_sort(self, *args):
        raise NotImplementedError()


class SmarketsBuilder(GenericBuilder):
    def special_sort(self, imports, from_imports, typ, pre_import, pre_from_import):
        output = ""
        for imp in sorted(imports[typ], key=_sorter):
            output += self._build(imp, pre_import[imp])

        for imp in sorted(from_imports[typ], key=_sorter):
            output += self._build(imp, pre_from_import[imp])

        return output


class GoogleBuilder(GenericBuilder):
    def special_sort(self, imports, from_imports, typ, pre_import, pre_from_import):
        output = ""
        for imp in sorted(imports[typ] + from_imports[typ], key=_sorter_unify_import_and_from):
            output += self._build(imp, pre_import.get(imp, pre_from_import.get(imp)))
        return output


class CryptoBuilder(GenericBuilder):
    def special_sort(self, imports, from_imports, typ, pre_import, pre_from_import):
        output = ""
        if typ in (STDLIB, FUTURE, RELATIVE):
            for imp in sorted(imports[typ], key=_sorter):
                output += self._build(imp, pre_import[imp])

            for imp in sorted(from_imports[typ], key=_sorter):
                output += self._build(imp, pre_from_import[imp])
        else:
            last_imp = ''
            for imp in sorted(imports[typ] + from_imports[typ], key=_sorter_unify_import_and_from):
                if not last_imp or not _get_core_import(imp).startswith(last_imp):
                    if last_imp:
                        if imp in pre_import:
                            pre_import.get(imp).append('')
                        if imp in pre_from_import:
                            pre_from_import.get(imp).append('')
                    last_imp = _get_core_import(imp)

                output += self._build(imp, pre_import.get(imp, pre_from_import.get(imp)))
        return output


class Rebuilder():
    def __init__(self, type='s', max_line_length=80, indent="    "):
        self.builder_object = _get_builder_func(type, int(max_line_length), indent)

    def rebuild(
            self, local_imports, pre_import, pre_from_import, lines_before_any_imports,
            after_imports
    ):
        imports_by_type = _classify_imports(pre_import.keys(), local_imports)
        from_imports_by_type = _classify_imports(pre_from_import.keys(), local_imports)
        return self.builder_object.do_all(
            imports_by_type, from_imports_by_type, lines_before_any_imports, pre_import,
            pre_from_import, after_imports
        )
