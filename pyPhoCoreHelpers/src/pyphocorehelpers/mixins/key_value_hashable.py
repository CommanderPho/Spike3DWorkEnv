from ..hashing_helpers import hash_dictionary

class KeyValueHashableObject:
    """ Objects can be hashed from the keys and values of their self.__dict__ """
    
    def __hash__(self):
        """ custom hash function that allows use in dictionary just based off of the values and not the object instance. """
        return hash_dictionary(self.__dict__)
