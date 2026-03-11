import numpy as np

class OptionsListMixin:
    """_summary_
 
    History:
        Refactored out of pyphoplacecellanalysis/PhoPositionalData/plotting/mixins/general_plotting_mixins.py on 2022-06-13
    """
    @staticmethod
    def options_to_str(options_list_ints):
        return [f'{i}' for i in options_list_ints]
    @staticmethod
    def options_to_int(options_list_strings):
        return [int(a_str) for a_str in options_list_strings]
    @staticmethod
    def build_pf_options_list(num_pfs=40):
        pf_options_list_ints = np.arange(num_pfs)
        pf_options_list_strings = OptionsListMixin.options_to_str(pf_options_list_ints) # [f'{i}' for i in pf_options_list_ints]
        return pf_options_list_ints, pf_options_list_strings