from __future__ import absolute_import, division, print_function

import re

IMPORT_LIB = r'^import\s+([\w\.]+)'
FROM_IMPORT_LIB = r'^from\s+([\w\.]+)\s+import'

TRIPLE_DOUBLE = '"""'
TRIPLE_SINGLE = "'''"


def strip_to_module_name(line):
    return re.match(IMPORT_LIB, line).groups()[0]


def strip_to_module_name_from_import(line):
    return re.match(FROM_IMPORT_LIB, line).groups()[0]


def is_hash_a_comment(s):
    return ("'" not in s or s.index('#') < s.index("'")) and ('"' not in s or s.index('#') < s.index('"'))


def get_doc_string_by_type2(s, quote_type):
    opposite_quote = {TRIPLE_DOUBLE: "'", TRIPLE_SINGLE: '"'}[quote_type]

    if '#' in s and s.index('#') < s.index(quote_type) and is_hash_a_comment(s):
        return len(s), False

    if opposite_quote in s and s.index(opposite_quote) < s.index(quote_type):
        return s.index(opposite_quote, s.index(opposite_quote) + 1) + 1, False  # fails on backslash '\''

    return s.index(quote_type), True


def get_part(s, base_index, quote):
    points = []
    index, in_quote = get_doc_string_by_type2(s, quote_type=quote)

    if in_quote:
        points.append((index + base_index, quote))
        s = s[index + 3:]
        base_index += index + 3
        try:
            points.append((s.index(quote) + 3 + base_index, quote))
            base_index += s.index(quote) + 3
            s = s[s.index(quote) + 3:]
        except ValueError:
            return "", base_index, points
    else:
        base_index += index
        s = s[index:]

    return s, base_index, points


def get_doc_string(s):
    points = []
    base_index = 0

    while s:
        double = s.find(TRIPLE_DOUBLE)
        single = s.find(TRIPLE_SINGLE)

        if double == single:
            break
        elif (double < single or single == -1) and double != -1:
            s, base_index, p2 = get_part(s, base_index, TRIPLE_DOUBLE)
            points += p2

        elif double > single or double == -1:
            s, base_index, p2 = get_part(s, base_index, TRIPLE_SINGLE)
            points += p2
        else:
            raise Exception('impossible')

    return points

#
# def get_doc_string_by_type(s, quote_type, from_point=0, in_doc_string=False):
#     s2 = s[from_point:]
#
#     opposite_quote = {TRIPLE_DOUBLE: "'", TRIPLE_SINGLE: '"'}[quote_type]
#
#     # pull out into different func?
#     if in_doc_string:
#         if quote_type in s2:
#             return '?', [from_point + s2.index(quote_type)] + get_doc_string_by_type(
#                 s, quote_type, from_point + s2.index(quote_type) + 3, in_doc_string=False
#             )
#         else:
#             return '', []
#
#     if quote_type not in s:
#         return '', []
#
#     # not if # is in a comment
#     if '#' in s2 \
#             and s2.index('#') < s2.index(quote_type) \
#             and (opposite_quote not in s2 or s2.index('#') < s2.index(opposite_quote)):
#         return '', []
#
#     if opposite_quote in s2 and s2.index(opposite_quote) < s2.index(quote_type):
#         return get_doc_string(s, from_point + s2.index(opposite_quote, s2.index(opposite_quote) + 1) + 1)
#
#     return quote_type, [from_point + s2.index(quote_type)] + get_doc_string_by_type(
#         s, quote_type, from_point + s2.index(quote_type) + 3, in_doc_string=True
#     )
