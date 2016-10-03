from __future__ import absolute_import, division, print_function

import re


IMPORT_LINE = r'^import\s+'
AFTER_SPACE = r'\s.*'
FROM_IMPORT_LINE = r'^from\s+'
AFTER_IMPORT = r'\s+import.*'


def strip_to_module_name(line):
    module_name = re.sub(IMPORT_LINE, "", line)
    module_name = re.sub(AFTER_SPACE, "", module_name)
    return module_name


def strip_to_module_name_from_import(line):
    module_name = re.sub(FROM_IMPORT_LINE, "", line)
    module_name = re.sub(AFTER_IMPORT, "", module_name)
    return module_name


def get_doc_string(s, from_point=0, in_doc_string=False):
    s2 = s[from_point:]

    # pull out into different func?
    if in_doc_string:
        if '\"\"\"' in s2:
            return [from_point + s2.index('\"\"\"')] + get_doc_string(
                s, from_point + s2.index('\"\"\"') + 3, in_doc_string=False
            )
        else:
            return []

    if '"""' not in s2:
        return []

    # not if # is in a comment
    if '#' in s2 \
            and s2.index('#') < s2.index('\"\"\"') \
            and ('\'' not in s2 or s2.index('#') < s2.index('\'')):
        return []

    if '\'' in s2 and s2.index('\'') < s2.index('\"\"\"'):
        return get_doc_string(s, from_point + s2.index('\'', s2.index('\'') + 1) + 1, in_doc_string=False)

    return [from_point + s2.index('\"\"\"')] + get_doc_string(
        s, from_point + s2.index('\"\"\"') + 3, in_doc_string=True
    )
