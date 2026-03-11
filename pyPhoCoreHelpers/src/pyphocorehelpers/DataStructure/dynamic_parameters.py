from collections.abc import MutableMapping
from pyphocorehelpers.mixins.diffable import DiffableObject

class DynamicParameters(DiffableObject, MutableMapping):
    """ A class that permits flexible prototyping of parameters and data needed for computations, while still allowing development-time guidance on available members.
    
        From https://treyhunner.com/2019/04/why-you-shouldnt-inherit-from-list-and-dict-in-python/#When_making_a_custom_list_or_dictionary,_remember_you_have_options
        
        The UserDict class implements the interface that dictionaries are supposed to have, but it wraps around an actual dict object under-the-hood.

        The UserList and UserDict classes are for when you want something that acts almost identically to a list or a dictionary but you want to customize just a little bit of functionality.

        The abstract base classes in collections.abc are useful when you want something that’s a sequence or a mapping but is different enough from a list or a dictionary that you really should be making your own custom class.


    TODO: Observed Issues:
    1. calling .copy() on this object doesn't work, KeyError: 'copy'
    2. pickling sometimes fails, KeyError: 'mro' - SOLUTION: Interestingly this only seems to happen if the top-level item to pickle is a DynamicParameters. Calling .to_dict() and then pickling works even if it has many nested children that are DynamicParameters
        FAILS with KeyError 'mro': `saveData(global_computation_results_pickle_path, (curr_active_pipeline.global_computation_results))`
        WORKS: `saveData(global_computation_results_pickle_path, (curr_active_pipeline.global_computation_results.to_dict()))`
    3. hasattr(plots, 'key') does not work correctly: WORKAROUND: instead of `hasattr(plots, 'root_plot')`, use `plots.has_attr('root_plot')` to avoid unhandled `KeyError: 'root_plot'`
    
    """
    debug_enabled = False
    outcome_on_item_not_found = None

    def __init__(self, **kwargs):
        self._mapping = {} # initialize the base dictionary object where things will be stored
        self._keys_at_init = list(kwargs.keys())
        self.update(kwargs)
       
    def __getitem__(self, key):
        if DynamicParameters.debug_enabled:
            print(f'DynamicParameters.__getitem__(self, key): key {key}')
        return self._mapping[key] #@IgnoreException

    def __delitem__(self, key):
        if DynamicParameters.debug_enabled:
            print(f'DynamicParameters.__delitem__(self, key): key {key}')
        del self._mapping[key]

    def __setitem__(self, key, value):
        if DynamicParameters.debug_enabled:
            print(f'DynamicParameters.__setitem__(self, key, value): key {key}, value {value}')
        self._mapping[key] = value

    def __iter__(self):
        return iter(self._mapping)
    def __len__(self):
        return len(self._mapping)
    def __repr__(self):
        return f"{type(self).__name__}({self._mapping})"

    # Extra/Extended
    def __dir__(self):
        if DynamicParameters.debug_enabled:
            print(f'DynamicParameters.__dir__(self)')
        return self.keys()


    def __or__(self, other):
        """ Used with vertical bar operator: |
        
        Usage:
            (_test_complete_spike_analysis_config | _test_partial_spike_analysis_config)    
        """
        if isinstance(other, (dict)):
            other_dict = other
        elif isinstance(other, DynamicParameters):
            other_dict = other.to_dict()
        else:
            # try to convert the other type into a dict using all known available methods: DynamicContainer
            try:
                other_dict = other.to_dict() # try to convert to dict using the .to_dict() method if possible
            except Exception as e:
                # If that failed, fallback to trying to access the object's .__dict__ property
                try:
                    other_dict = dict(other.items())
                except Exception as e:
                    # Give up, can't convert!                
                    print(f'UNHANDLED TYPE: type(other): {type(other)}, other: {other}')
                    # raise NotImplementedError            
                    other_dict = None
                    raise e

                pass # other_dict               
        
        dict_or = self.to_dict().__or__(other_dict)
        return DynamicParameters.init_from_dict(dict_or)
        
    def __getattr__(self, item):
        """
            NOTE: instead of `hasattr(plots, 'root_plot')`, use `plots.has_attr('root_plot')` to avoid unhandled `KeyError: 'root_plot'`
            
        """
        # Gets called when the item is not found via __getattribute__
        if DynamicParameters.debug_enabled:
            print(f'DynamicParameters.__getattr__(self, item): item {item}')
        try:
            # try to return the value of the dictionary 
            return self[item]
        except KeyError as err:
            if DynamicParameters.debug_enabled:
                print(f"DynamicParameters.__getattr__(self, item: {item}) KeyError: Attribute could not be found in dictionary either!\n\t KeyError: {err}")
            # if DynamicParameters.outcome_on_item_not_found:
            # return super(DynamicParameters, self).__setattr__(item, 'orphan')
            if item == '__deepcopy__':
                # As described here: https://stackoverflow.com/questions/33387801/why-does-deepcopy-fail-with-keyerror-deepcopy-when-copying-custom-objec to enable deepcopy(...) on the object
                raise AttributeError(item)      #@IgnoreException               
            else:
                raise
        # except AttributeError as err:
        #     print(f"AttributeError: {err}")
        #     return super(DynamicParameters, self).__setattr__(item, 'orphan')
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
            raise

    def __setattr__(self, attr, value):
        if attr == '__setstate__':
            return lambda: None
        elif ((attr == '_mapping') or (attr == '_keys_at_init')):
            # Access to the raw data variable
            # object.__setattr__(self, name, value)
            super(DynamicParameters, self).__setattr__(attr, value) # call super for valid properties
            # self._mapping = value # this would be infinitely recurrsive!
        else:
            if DynamicParameters.debug_enabled:
                print(f'DynamicParameters.__setattr__(self, attr, value): attr {attr}, value {value}')
            self[attr] = value

    # def _original_attributes():
    #     self._keys_at_init
    
    @property
    def all_attributes(self):
        """Any attributes on the object. """
        return list(self.keys())
    
    @property
    def original_attributes(self):
        """The attributes that were provided initially at init. """
        return self._keys_at_init
    
    @property
    def dynamically_added_attributes(self):
        """The attributes that were added dynamically post-init."""
        return list(set(self.all_attributes) - set(self.original_attributes))
    
    
    def has_attr(self, key):
        return key in self.all_attributes

    def __hash__(self):
        """ custom hash function that allows use in dictionary just based off of the values and not the object instance. """
        # return hash((self.age, self.name))
        member_names_tuple = list(self.keys())
        values_tuple = list(self.values())
        combined_tuple = tuple(member_names_tuple + values_tuple)
        return hash(combined_tuple)
    
        
    # For diffable parameters:
    def diff(self, other_object):
        return DiffableObject.compute_diff(self, other_object)


    def to_dict(self):
        return dict(self.items())
        
    # Helper initialization methods:    
    # For initialization from a different dictionary-backed object:
    @classmethod
    def init_from_dict(cls, a_dict):
        # NOTE: encounter `TypeError: keywords must be strings` when a_dict has keys other than strings.
        try:
            return cls(**a_dict) # expand the dict as input args.       #@IgnoreException
        except TypeError as e:
            # `TypeError: keywords must be strings` when trying to ** expand a_dict with non-string keys
            new = cls()
            for k,v in a_dict.items():
                new[k] = v
            return new
        except Exception as e:
            raise e
    
    @classmethod
    def init_from_object(cls, an_object):
        # test to see if the object is dict-backed:
        obj_dict_rep = an_object.__dict__
        return cls.init_from_dict(obj_dict_rep)
    
    ## For serialization/pickling:
    def __getstate__(self):
        # Copy the object's state from self.__dict__ which contains
        # all our instance attributes (_mapping and _keys_at_init). Always use the dict.copy()
        # method to avoid modifying the original state.
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        # del state['file']
        return state

    def __setstate__(self, state):
        # Restore instance attributes (i.e., _mapping and _keys_at_init).
        self.__dict__.update(state)
        
