MAX_REPS = 3


def reduce_text(text):
    accumulator = []

    last_char = None
    last_count = 0
    for actual_char in text:
        if last_char != actual_char:
            last_count = 0
            last_char = actual_char

        last_count += 1

        if last_count > MAX_REPS:
            continue

        accumulator.append(actual_char)

    return "".join(accumulator)
