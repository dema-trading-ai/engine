from collections import defaultdict


def group_by(arr, key: str):
    group = defaultdict(list)

    for item in arr:
        group[getattr(item, key)].append(item)
    return group
