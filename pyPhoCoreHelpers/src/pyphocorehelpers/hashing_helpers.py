
def freeze(d):
    """ recursively freezes dicts with nested dict/list elements so they may be hashed """
    if isinstance(d, dict):
        return frozenset((key, freeze(value)) for key, value in d.items())
    elif isinstance(d, list):
        return tuple(freeze(value) for value in d)
    return d


def get_hash_tuple(a_dict, included_keys=None):
    """ Helps in hashing a dictionary by flattening it to a flat list of its keys and values, and then converting it into a tuple (which is what the hash function expects). """
    if included_keys is not None:
        a_dict = {included_key:a_dict[included_key] for included_key in included_keys} # filter the dictionary for only the keys specified

    member_names_tuple = list(a_dict.keys())
    values_tuple = list(a_dict.values())
    combined_tuple = tuple(member_names_tuple + values_tuple)
    return combined_tuple


def hash_dictionary(a_dict):
    """ Hashes a dictionary from its keys and values. All members must be hashable themselves. """
    return hash(get_hash_tuple(a_dict))

