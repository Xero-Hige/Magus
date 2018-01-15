# Based on: https://gist.github.com/topicus/4611549
# Updated on 13/11/2017 with ñ skip

import unicodedata


def strip_accents(s):
    stripped = [c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn']
    # for i in range(len(stripped)):  TODO: CHECK
    #    if stripped[i] == 'Ñ' or stripped[i] == 'ñ':
    #        stripped[i] = s[i]
    return "".join(stripped)
