REP_SIZE = 3


def preprocess(word, rep_size=REP_SIZE):
    """ """
    if not word:
        return (word, False)

    aux_buffer = []
    rep_window = ["" for _ in range(rep_size)]

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

    return ("".join(aux_buffer), False)


print (preprocess("Jaaaaaaaaaaaaaaajajajoooojooo"))
