__author__ = 'tolkjen'


def lists_equiv(a, b):
    """
    If a and b contain the same elements (order not important) returns True. False otherwise.
    :param a: First list
    :param b: Second list
    :return: Above.
    """
    def sort_recursive(objects):
        for obj in objects:
            if isinstance(obj, list):
                sort_recursive(obj)
        objects.sort()
    a_copy = a[:]
    sort_recursive(a_copy)
    b_copy = b[:]
    sort_recursive(b_copy)
    return a_copy == b_copy
