from collections import ChainMap, OrderedDict
import numpy as np
from copy import deepcopy
import matplotlib as mpl
import matplotlib.pyplot as plt

from ..mixins.diffable import DiffableObject
from ..mixins.key_value_hashable import KeyValueHashableObject

from ..print_helpers import SimplePrintable

# ## Unused, doesn't work
# # Python3 code to demonstrate working of
# # Symmetric Difference of Multiple sets
# # Using Counter() + chain.from_iterable() + items()
# from collections import Counter
# from itertools import chain
  
# def symmetric_diff_multiple_sets(list_of_sets):
#     # clubbing operations using items() to get items 
#     return {key for key, val in Counter(chain.from_iterable(list_of_sets)).items() if val == 1}


"""" 
I think this isn't used anywhere? I'm not sure though.


"""

class DeepChainMap(ChainMap):
    'Variant of ChainMap that allows direct updates to inner scopes'

    def __setitem__(self, key, value):
        for mapping in self.maps:
            if key in mapping:
                mapping[key] = value
                return
        self.maps[0][key] = value

    def __delitem__(self, key):
        for mapping in self.maps:
            if key in mapping:
                del mapping[key]
                return
        raise KeyError(key)
    
    

class UniqueCombinedConfigIdentifier(SimplePrintable, DiffableObject, KeyValueHashableObject):
    """ Note: this is not general, it's for the place cell project, and it combines a bunch of functionality. """
    def __init__(self, filter_name, active_config, variant_identifier_label=None, **kwargs):
        combined_config_dict = UniqueCombinedConfigIdentifier._build_combined_identifier(filter_name, active_config, variant_identifier_label=variant_identifier_label)
        for key, value in combined_config_dict.items():
            setattr(self, key, value) # add each of the combined items built from the separate configs

        # Dump all arguments into parameters.
        for key, value in kwargs.items():
            setattr(self, key, value)


    def items(self):
        """ Passthrough for use with DiffableObject """
        return self.__dict__.items()


    @classmethod
    def init_from_combined_dict(cls, combined_config_dict):
        return cls(**combined_config_dict)

    @staticmethod
    def _build_combined_identifier(filter_name, active_config, variant_identifier_label=None, debug_print=False):
        """ Build the combined indentifier dictionary which includes elements from the session, the function that was used to filter the session, and of course the computation config """
        combined_config_dict = {**{included_key:active_config.active_session_config.__dict__[included_key] for included_key in ['session_name']}, **active_config.computation_config.__dict__, 'filter_name':filter_name, **active_config.filter_config} # include all elements of the computation config
        if variant_identifier_label is not None:
            combined_config_dict[variant_identifier_label] = variant_identifier_label
        # combined_config_hash = hash_dictionary(combined_config_dict)
        # print(f'active_config.active_session_config: {active_config.active_session_config}')
        if debug_print:
            print(f'combined_config_dict: {combined_config_dict}\n')
        return combined_config_dict



class PhoHistoricalResultsManager(SimplePrintable):
    """ Keeps track of historical results and allows you to compare them easily. """
    def __init__(self, results_dict = OrderedDict(), outputs_dict = OrderedDict()):
        super(PhoHistoricalResultsManager, self).__init__()
        self.results = results_dict
        self.outputs = outputs_dict
        
    
    def add(self, current_config, current_results=dict(), current_outputs=dict()):
        if current_config in self.results:
            print('already exists!')
            self.results[current_config] = (self.results[current_config] | current_results) # adds/replaces the result if needed
        else:
            print('new config! adding results!')
            self.results[current_config] = current_results
            
        if current_config in self.outputs:
            print('already exists!')
            self.outputs[current_config] = (self.outputs[current_config] | current_outputs) # adds/replaces the result if needed
        else:
            print('new config! adding outputs!')
            self.outputs[current_config] = current_outputs
            
    def reset(self):
        print(f'Resetting PhoHistoricalResultsManager!')
        self.results = OrderedDict()
        self.outputs = OrderedDict()
        


    def minimal_differences(self):
        historical_configs = list(self.outputs.keys())
        # historical_config_sets = [set(a_config.__dict__.items()) for a_config in historical_configs]
        historical_config_sets = [set(a_config.items()) for a_config in historical_configs]
        historical_changed_lists = []
        historical_unchanged_lists = []
        for i in np.arange(start=1, stop=len(historical_configs)):
            changed_set = historical_config_sets[i].symmetric_difference(historical_config_sets[i-1])
            unchanged_set = historical_config_sets[i].intersection(historical_config_sets[i-1])
            # historical_diff_lists.append(diff_list) # in this mode, the output is then a list of sets
            diff_changes_dictionary = PhoHistoricalResultsManager.build_difference_dictionary(list(changed_set))
            historical_changed_lists.append(diff_changes_dictionary)
            historical_unchanged_lists.append(unchanged_set)
        
        return historical_changed_lists
    
    
    @staticmethod
    def build_difference_dictionary(flat_list):
        # compute_diff
        ''' the output of diffing is a list like [('filter_name', 'maze1'),
        ('filter_function',
        <function __main__.build_any_maze_epochs_filters.<locals>.<lambda>(x)>),
        ('filter_name', 'maze'),
        ('filter_function',
        <function __main__.build_any_maze_epochs_filters.<locals>.<lambda>(x)>)]
        Using the the fact that included differing elements are repeated all for the first list's values, and then again for the second list. 
        '''
        middle_index = len(flat_list)//2
        assert(np.mod(len(flat_list), 2) == 0)
        first_half = flat_list[:middle_index]
        second_options = flat_list[middle_index:]

        changed_item_labels = [an_item[0] for an_item in first_half] # ['filter_name', 'filter_function']
        changed_item_values_lhs = [an_item[1] for an_item in first_half] # the values for each item from the lhs object
        changed_item_values_rhs = [an_item[1] for an_item in second_options]
        # A dictionary containing a tuple of the different options for each key, where the key is the differing item's label:
        # changed_item_dict = {a_label: (lhs_v, rhs_v) for (a_label, lhs_v, rhs_v) in zip(changed_item_labels, changed_item_values_lhs, changed_item_values_rhs)}
        changed_item_dict = OrderedDict({a_label: (lhs_v, rhs_v) for (a_label, lhs_v, rhs_v) in zip(changed_item_labels, changed_item_values_lhs, changed_item_values_rhs)})
        """ changed_item_dict
        {'filter_name': ('maze1', 'maze'),
        'filter_function': (<function __main__.build_any_maze_epochs_filters.<locals>.<lambda>(x)>,
        <function __main__.build_any_maze_epochs_filters.<locals>.<lambda>(x)>)}
        """
        return changed_item_dict



    def print_change_log(self):
        """ prints the log/record of changes for all entries. """
        historical_diff_lists = self.minimal_differences()
        num_change_steps = len(historical_diff_lists)
        print(f'PhoHistoricalResultsManager<{num_change_steps}>:')
        for step_i in np.arange(stop=num_change_steps):
            curr_change = historical_diff_lists[step_i] # the dict containing the change information for each step
            curr_changed_property_names = list(curr_change.keys())
            print(f'\t change[{step_i}]: {curr_changed_property_names}')
            
        print(f'end.')
        

    # iPython/Jupyter Pretty-printing display:
    def _repr_pretty_(self, p, cycle):
        if cycle:
            p.text('UniqueCombinedConfigIdentifier(...)')
        else:
            p.text('UniqueCombinedConfigIdentifier[...]')
