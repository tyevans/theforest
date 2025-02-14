def wordwrap(s, col_width=80):
    output = []
    for i in range(0, len(s), col_width):
        output.append(s[i : i + col_width])
    return "\n  ".join(output)
