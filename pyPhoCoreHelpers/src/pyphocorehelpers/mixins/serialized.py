from copy import deepcopy
# Safelist (Allowlist) and Blocklist


class SerializedAttributesAllowBlockSpecifyingClass:
    """ 2023-04-14 - Implements two potential classmethods that returns an allowlist or denylist of serialized_keys, allowing the implementor to specify which keys will be serialized/deserialized. 
        Useful for ignoring computed values, etc.

        Aims to completely replace `SerializedAttributesSpecifyingClass`

        from pyphocorehelpers.mixins.serialized import SerializedAttributesAllowBlockSpecifyingClass
    """
    @classmethod
    def serialized_key_blocklist(cls):
        """ specifies specific keys NOT to serialize (to remove before serialization). If `serialized_key_allowlist` is specified, this variable will be ignored. """
        return [] # no keys by default

    @classmethod
    def serialized_key_allowlist(cls):
        """ If specified, ONLY THE KEYS SPECIFIED will be serialized. Overrides `serialized_key_blocklist`  """
        return None # do not specify an allowlist by default (allowing all keys or those not specified in `serialized_key_blocklist`
    
    # @classmethod
    # def from_dict(cls, val_dict):
    #     new_obj = BayesianPlacemapPositionDecoder(time_bin_size=val_dict.get('time_bin_size', 0.25), pf=val_dict.get('pf', None), spikes_df=val_dict.get('spikes_df', None), setup_on_init=val_dict.get('setup_on_init', True), post_load_on_init=val_dict.get('post_load_on_init', False), debug_print=val_dict.get('debug_print', False))
    #     return new_obj

    @classmethod
    def serialization_perform_drop_blocklist(cls, state_dict:dict) -> dict:
        """ drops the attributes specified in `serialized_key_blocklist` from the state_dict (which can come from self.__dict__) and returns the resultant dict. """
        # state_dict = deepcopy(state_dict)
        state_dict = state_dict.copy()
        assert cls.serialized_key_allowlist() is None, f"If `serialized_key_allowlist` is specified, this variable will be ignored. serialized_key_allowlist: {cls.serialized_key_allowlist()}"
        for a_blocked_key in cls.serialized_key_blocklist():
            state_dict.pop(a_blocked_key)
        return state_dict


    # @classmethod
    # def serialized_keys(cls):
    #     """ Allows overriding to directly specify the keys to be serialized, or allowing them to be created from `serialized_key_allowlist` and `serialized_key_blocklist` """
    #     included_keys = []
    #     if cls.serialized_key_allowlist is not None:
    #         # Only use the allow list
    #         included_keys.extend(cls.serialized_key_allowlist)
    #     else:
    #         # no allowlist specified
    #         state = cls.serialization_perform_drop_blocklist(self.__dict__.copy())


    def to_dict(self):
        if self.serialized_key_allowlist() is not None:
            # Only use the allow list
            state = {}
            for an_included_key in self.serialized_key_allowlist():
                state[an_included_key] = self.__dict__[an_included_key]
        else:
            # no allowlist specified
            state = self.serialization_perform_drop_blocklist(deepcopy(self.__dict__))

        return state

