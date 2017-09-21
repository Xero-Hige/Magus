REP_SIZE = 3


def preprocess(word):
    """ """
    if not word:
        return word, False

    aux_buffer = []
    rep_window = ["" for _ in range(REP_SIZE)]

    for c in word:
        buffer_exceed = True
        for window_c in rep_window:
            if c != window_c:
                buffer_exceed = False
                break

        if buffer_exceed:
            continue

        aux_buffer.append(c)

        rep_window = rep_window[1:]
        rep_window.append(c)

    return "".join(aux_buffer), False
