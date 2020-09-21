def average_color(colors):
    """
    Returns average for the list, or None of the list is empty. Each element is
    an inner list of 4 numbers.
    """
    count = len(colors)
    if count == 0:
        return None
    totals = [0, 0, 0, 0]
    for color in colors:
        for i in range(0, 4):
            totals[i] += color[i]
    avg = []
    for i in range(0, 4):
        avg.append(round(totals[i] / count))
    return avg

def rounded_color(color):
    return [round(c) for c in color]
