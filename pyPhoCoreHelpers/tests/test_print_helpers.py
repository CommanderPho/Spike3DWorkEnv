import unittest
import numpy as np
import pandas as pd
# import the package
import sys, os
from pathlib import Path

# Add Neuropy to the path as needed
tests_folder = Path(os.path.dirname(__file__))

try:
    import pyphocorehelpers
except ModuleNotFoundError as e:    
    root_project_folder = tests_folder.parent
    print('root_project_folder: {}'.format(root_project_folder))
    src_folder = root_project_folder.joinpath('src')
    pyphocorehelpers_folder = src_folder.joinpath('pyphocorehelpers')
    print('pyphocorehelpers_folder: {}'.format(pyphocorehelpers_folder))
    sys.path.insert(0, str(src_folder))
finally:
    from pyphocorehelpers.print_helpers import print_value_overview_only

class TestPrintHelperMethods(unittest.TestCase):
    """ 

    <numpy.ndarray; shape: (15,)>
    <list; shape: (15,)>
    WARNING: value_shape is ().
    <int; shape: scalar>
    WARNING: value_shape is ().
    <str; shape: 11>
    WARNING: value_shape is ().
    <dict; shape: 2>

    """
    def setUp(self):
        # Hardcoded:
        self.integer_value = 9
        self.string_value = 'test_string'
        self.native_list = list(range(15))
        self.numpy_list = np.arange(15)
        self.dict_value = {'key1': 0.34, 'key2': 'a'}
        self.pandas_dataframe = pd.DataFrame({'a': np.arange(99), 'b': (3.0*np.arange(99))})
        
    def tearDown(self):
        self.integer_value = None
        self.string_value = None
        self.native_list = None
        self.numpy_list = None
        self.dict_value = None
        self.pandas_dataframe = None
        

    def test_print_value_overview_only_integer_scalar(self):
        out_str = print_value_overview_only(self.integer_value, should_return_string=True)
        self.assertEqual(out_str, '<int; shape: scalar>', f'FAIL. out_str: {out_str}')

    def test_print_value_overview_only_string_scalar(self):
        out_str = print_value_overview_only(self.string_value, should_return_string=True)
        self.assertEqual(out_str, '<str; shape: 11>', f'FAIL. out_str: {out_str}')
        
    def test_print_value_overview_only_native_list_value(self):
        out_str = print_value_overview_only(self.native_list, should_return_string=True)
        self.assertEqual(out_str, '<list; shape: (15,)>', f'FAIL. out_str: {out_str}')
        
    def test_print_value_overview_only_numpy_array(self):
        out_str = print_value_overview_only(self.numpy_list, should_return_string=True)
        self.assertEqual(out_str, '<numpy.ndarray; shape: (15,)>', f'FAIL. out_str: {out_str}')
        
    def test_print_value_overview_only_dict_value(self):
        out_str = print_value_overview_only(self.dict_value, should_return_string=True)
        self.assertEqual(out_str, '<dict; shape: 2>', f'FAIL. out_str: {out_str}')
        
    def test_print_value_overview_only_pandas_dataframe(self):
        out_str = print_value_overview_only(self.pandas_dataframe, should_return_string=True)
        self.assertEqual(out_str, '<pandas.core.frame.DataFrame; shape: (99, 2)>', f'FAIL. out_str: {out_str}')
        


if __name__ == '__main__':
    unittest.main()
    
    