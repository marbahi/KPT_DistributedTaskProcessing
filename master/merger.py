def merge_sorted_chunks(chunks, mode='ascending'):
    result = []
    for chunk in chunks:
        result.extend(chunk)
    if mode == 'ascending':
        result.sort()
    else:
        result.sort(reverse=True)
    return result
