# Based on: https://gist.github.com/topicus/4611549
# Updated on 13/11/2017 with ñ skip

import sys
import unicodedata


def strip_accents(s):
    stripped = [c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn']
    try:
        for i in range(len(stripped)):
            if s[i] == 'Ñ' or s[i] == 'ñ':
                stripped[i] = s[i]

    except IndexError as e:
        print("Wrong strip: {} caused by {}".format(e, s), file=sys.stderr)

    return "".join(stripped)
