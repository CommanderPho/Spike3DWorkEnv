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
    from pyphocorehelpers.DataStructure.dynamic_parameters import DynamicParameters



class TestDynamicParametersMethods(unittest.TestCase):

    def setUp(self):
        self.test1 = DynamicParameters()
        self.test2 = DynamicParameters(prop0=9, prop1='tree', prop2='JORB', prop9=list())

    def tearDown(self):
        self.test1 = None
        self.test2 = None

    def test_empty_params(self):
        self.assertEqual(len(self.test1.keys()), 0, f'Should have zero members but instead has {len(self.test1.keys())}')

    # def test_empty_params_add_member(self):
    #     self.assertEqual(len(self.test.keys()))

    def test_initialized_with_members(self):
        self.assertSequenceEqual(list(self.test2.keys()), ['prop0', 'prop1', 'prop2', 'prop9'], f'Should be equal: list(test2.keys()): {list(self.test2.keys())} and [prop0, prop1, prop2, prop9].')
        # self.assertDictEqual
        
    # def test_computation_config_hashing(self):
    #     ## Hash testing:
    #     obj1 = PlacefieldComputationParameters(speed_thresh=15.0, grid_bin=None, smooth=(1.0, 1.0), frate_thresh=0.2, time_bin_size=0.5)
    #     obj2 = PlacefieldComputationParameters(speed_thresh=15.0, grid_bin=None, smooth=(1.0, 1.0), frate_thresh=0.2, time_bin_size=0.5)
    #     self.assertEqual(obj1, obj2, f'The hashes of two objects with the same values should be equal, but: hash(obj1): {hash(obj1)}, hash(obj2): {hash(obj2)}!')
    

if __name__ == '__main__':
    unittest.main()
    
    