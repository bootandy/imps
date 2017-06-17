from __future__ import absolute_import, division, print_function

IMPORT_LIB = r'^import\s+([\w\.]+)'
FROM_IMPORT_LIB = r'^from\s+([\w\.]+)\s+import'

TRIPLE_DOUBLE = '"""'
TRIPLE_SINGLE = "'''"


def _is_hash_a_comment(s):
    return ("'" not in s or s.index('#') < s.index("'")) and ('"' not in s or s.index('#') < s.index('"'))


def _get_doc_string_by_type(s, quote_type):
    opposite_quote = {TRIPLE_DOUBLE: "'", TRIPLE_SINGLE: '"'}[quote_type]

    if '#' in s and s.index('#') < s.index(quote_type) and _is_hash_a_comment(s):
        return len(s), False

    if opposite_quote in s and s.index(opposite_quote) < s.index(quote_type):
        return s.index(opposite_quote, s.index(opposite_quote) + 1) + 1, False  # fails on backslash '\''

    return s.index(quote_type), True


def _get_part(s, base_index, quote):
    points = []
    index, in_quote = _get_doc_string_by_type(s, quote_type=quote)

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

        if double == single == -1:
            break
        elif (double < single or single == -1) and double != -1:
            s, base_index, p2 = _get_part(s, base_index, TRIPLE_DOUBLE)
            points += p2

        elif double > single or double == -1:
            s, base_index, p2 = _get_part(s, base_index, TRIPLE_SINGLE)
            points += p2
        else:
            raise Exception('impossible')

    return points
