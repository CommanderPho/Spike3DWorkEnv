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
    from pyphocorehelpers.indexing_helpers import get_bin_centers, get_bin_edges, BinningInfo, compute_spanning_bins, build_spanning_grid_matrix, interleave_elements, np_ffill_1D, np_bfill_1D # , np_ffill

        
def random_array():
    choices = [1, 2, 3, 4, 5, 6, 7, 8, 9, np.nan]
    out = np.random.choice(choices, size=(1000, 10))
    return out


class TestIndexingMethods(unittest.TestCase):

    def setUp(self):
        # Hardcoded:
        self.integer_bin_edges = np.array([0, 1, 2, 3, 4, 5])
        self.float_bin_edges = np.array([0.1, 1.1, 2.1, 3.1, 4.1, 5.1])
        self.test_x_values = np.array([ 25.81175029,  29.58859215,  33.36543401,  37.14227587,
                40.91911773,  44.69595959,  48.47280146,  52.24964332,
                56.02648518,  59.80332704,  63.5801689 ,  67.35701076,
                71.13385263,  74.91069449,  78.68753635,  82.46437821,
                86.24122007,  90.01806194,  93.7949038 ,  97.57174566,
            101.34858752, 105.12542938, 108.90227124, 112.67911311,
            116.45595497, 120.23279683, 124.00963869, 127.78648055,
            131.56332241, 135.34016428, 139.11700614, 142.893848  ,
            146.67068986, 150.44753172, 154.22437359, 158.00121545,
            161.77805731, 165.55489917, 169.33174103, 173.10858289,
            176.88542476, 180.66226662, 184.43910848, 188.21595034,
            191.9927922 , 195.76963406, 199.54647593, 203.32331779,
            207.10015965, 210.87700151, 214.65384337, 218.43068524,
            222.2075271 , 225.98436896, 229.76121082, 233.53805268,
            237.31489454, 241.09173641, 244.86857827, 248.64542013,
            252.42226199, 256.19910385, 259.97594571, 263.75278758])

        self.test_y_values = np.array([124.38134129, 125.42466822, 126.46799515, 127.51132208,
            128.55464901, 129.59797594, 130.64130287, 131.6846298 ,
            132.72795673, 133.77128366, 134.8146106 , 135.85793753,
            136.90126446, 137.94459139, 138.98791832, 140.03124525,
            141.07457218, 142.11789911, 143.16122604, 144.20455297,
            145.2478799 , 146.29120684, 147.33453377, 148.3778607 ,
            149.42118763, 150.46451456, 151.50784149, 152.55116842,
            153.59449535])
        # unit_specific_binned_spike_counts, out_digitized_variable_bins, out_binning_info = ZhangReconstructionImplementation.time_bin_spike_counts_N_i(sess.spikes_df.copy(), time_bin_size, debug_print=debug_print) # unit_specific_binned_spike_counts.to_numpy(): (40, 85841)
        
        
        self.test_interleave_elements = {
            'string_elements': (['A','B','C','D'], ['a','b','c','d'], ['A', 'a', 'B', 'b', 'C', 'c', 'D', 'd']),
            'float_elements': ([0, 1, 2, 3], [1000,1001,1002,1003], [0, 1000, 1, 1001, 2, 1002, 3, 1003]),
            'nparrays': (np.array([0, 1, 2, 3]), np.array([1000,1001,1002,1003]), [0, 1000, 1, 1001, 2, 1002, 3, 1003]),
            'nparrays_transposed': (np.array([0, 1, 2, 3]).T, np.array([1000,1001,1002,1003]).T, [0, 1000, 1, 1001, 2, 1002, 3, 1003]),
            'points': (np.array([[0, 1, 2, 3], [0, 1, 2, 3]]).T, np.array([[1000,1001,1002,1003], [1000,1001,1002,1003]]).T, np.array([[   0,    0],
                [1000, 1000],
                [   1,    1],
                [1001, 1001],
                [   2,    2],
                [1002, 1002],
                [   3,    3],
                [1003, 1003]])),
        }
        
        

    def tearDown(self):
        self.integer_bin_edges=None
        self.float_bin_edges = None
        self.test_x_values = None
        self.test_y_values = None
        self.test_interleave_elements = None
        


    # def test_time_bin_spike_counts_N_i(self, out_digitized_variable_bins, out_binning_info):
    #     np.shape(out_digitized_variable_bins) # (85842,), array([  22.30206346,   22.32206362,   22.34206378, ..., 1739.09557005, 1739.11557021, 1739.13557036])
    #     assert out_digitized_variable_bins[-1] == out_binning_info.variable_extents[1], "out_digitized_variable_bins[-1] should be the maximum variable extent!"
    #     assert out_digitized_variable_bins[0] == out_binning_info.variable_extents[0], "out_digitized_variable_bins[0] should be the minimum variable extent!"

    def test_get_bin_centers(self):
        bin_centers = get_bin_centers(self.integer_bin_edges)
        self.assertEqual((np.shape(self.integer_bin_edges)[0] - 1), np.shape(bin_centers)[0], 'bin_centers should be one element smaller than bin_edges')

    def test_get_bin_edges(self):
        bin_centers = get_bin_centers(self.integer_bin_edges)
        recovered_bin_edges = get_bin_edges(bin_centers)
        self.assertSequenceEqual(recovered_bin_edges.tolist(), self.integer_bin_edges.tolist())
        
        
    def test_get_bin_centers_floats(self):
        bin_centers = get_bin_centers(self.float_bin_edges)
        self.assertEqual((np.shape(self.float_bin_edges)[0] - 1), np.shape(bin_centers)[0], 'bin_centers should be one element smaller than bin_edges')
        
    def test_get_bin_edges_floats(self):
        bin_centers = get_bin_centers(self.float_bin_edges)
        recovered_bin_edges = get_bin_edges(bin_centers)
        # self.assertSequenceEqual(recovered_bin_edges.tolist(), self.float_bin_edges.tolist())
        self.assertTrue(np.isclose(recovered_bin_edges, self.float_bin_edges).all())
        
        
        
        
        
    def test_build_spanning_grid_matrix(self):

        all_positions_matrix, flat_all_positions_matrix, original_data_shape = build_spanning_grid_matrix(self.test_x_values, self.test_y_values)
        # all_positions_matrix[0,0,:] # array([ 25.81175029, 124.38134129])
        print(f'all_positions_matrix[0,:,:]: {np.shape(all_positions_matrix[0,:,:])}') # constant x value, spans over all y-values
        self.assertListEqual(list(all_positions_matrix[0,:,1]), list(self.test_y_values), f'should be constant x value, spans over all y-values')
        # np.shape(all_positions_matrix[0,:,:]) # (29, 2)
        self.assertListEqual(list(all_positions_matrix[:,0,0]), list(self.test_x_values), f'should be constant y value, spans over all x-values')

        self.assertEqual(np.shape(all_positions_matrix)[2], 2, "third dimension should be of size 2 (for x, y coords)")
        # all_positions_matrix[:,0,:] # constant y value, spans over all x-values. 
        # np.shape(all_positions_matrix[:,0,:]) # (64, 2)

        # P_x = np.reshape(pf.occupancy, (-1, 1)) # occupancy gives the P(x) in general.
        # F = np.hstack(F_i) # Concatenate each individual F_i to produce F

    def test_compute_spanning_bins_num_bins_mode(self):
        fixed_num_bins = 32
        active_position_extents = np.array([23.92332935, 261.86436665])
        out_digitized_variable_bins, out_binning_info = compute_spanning_bins(active_position_extents, num_bins=fixed_num_bins)
        self.assertEqual(fixed_num_bins, out_binning_info.num_bins, f"out_binning_info.num_bins ({out_binning_info.num_bins}) must be equal to fixed_num_bins ({fixed_num_bins})! ")
        self.assertEqual(fixed_num_bins, np.shape(out_digitized_variable_bins)[0], f"np.shape(out_digitized_variable_bins)[0] ({np.shape(out_digitized_variable_bins)[0]}) must be equal to fixed_num_bins ({fixed_num_bins})! ")
        # Extents matching:
        self.assertEqual(out_digitized_variable_bins[-1], out_binning_info.variable_extents[1], "out_digitized_variable_bins[-1] should be the maximum variable extent!")
        self.assertEqual(out_digitized_variable_bins[0], out_binning_info.variable_extents[0], "out_digitized_variable_bins[0] should be the minimum variable extent!")
        self.assertEqual(active_position_extents[-1], out_binning_info.variable_extents[1], "active_position_extents[-1] should be the maximum variable extent!")
        self.assertEqual(active_position_extents[0], out_binning_info.variable_extents[0], "active_position_extents[0] should be the minimum variable extent!")
        print(f'test_compute_spanning_bins_num_bins_mode(): out_digitized_variable_bins: {out_digitized_variable_bins}, out_binning_info: {out_binning_info}')
        
        
        # Y position:
        active_position_extents = np.array([87.58388756, 153.31348421])
        out_digitized_variable_bins, out_binning_info = compute_spanning_bins(active_position_extents, num_bins=fixed_num_bins)
        self.assertEqual(fixed_num_bins, out_binning_info.num_bins, f"out_binning_info.num_bins ({out_binning_info.num_bins}) must be equal to fixed_num_bins ({fixed_num_bins})! ")
        self.assertEqual(fixed_num_bins, np.shape(out_digitized_variable_bins)[0], f"np.shape(out_digitized_variable_bins)[0] ({np.shape(out_digitized_variable_bins)[0]}) must be equal to fixed_num_bins ({fixed_num_bins})! ")
        # Extents matching:
        self.assertEqual(out_digitized_variable_bins[-1], out_binning_info.variable_extents[1], "out_digitized_variable_bins[-1] should be the maximum variable extent!")
        self.assertEqual(out_digitized_variable_bins[0], out_binning_info.variable_extents[0], "out_digitized_variable_bins[0] should be the minimum variable extent!")
        self.assertEqual(active_position_extents[-1], out_binning_info.variable_extents[1], "active_position_extents[-1] should be the maximum variable extent!")
        self.assertEqual(active_position_extents[0], out_binning_info.variable_extents[0], "active_position_extents[0] should be the minimum variable extent!")
        print(f'test_compute_spanning_bins_num_bins_mode(): out_digitized_variable_bins: {out_digitized_variable_bins}, out_binning_info: {out_binning_info}')


        
    def test_compute_spanning_bins_bin_size_mode(self):
        active_position_extents = np.array([23.92332935, 261.86436665])
        fixed_bin_size = 5.0
        out_digitized_variable_bins, out_binning_info = compute_spanning_bins(active_position_extents, bin_size=fixed_bin_size)
        print(f'test_compute_spanning_bins_bin_size_mode(): out_digitized_variable_bins: {out_digitized_variable_bins}, np.shape(out_digitized_variable_bins): {np.shape(out_digitized_variable_bins)}, out_binning_info: {out_binning_info}')
        self.assertEqual(out_binning_info.num_bins, np.shape(out_digitized_variable_bins)[0], f"out_binning_info.num_bins ({out_binning_info.num_bins}) must be equal to np.shape(out_digitized_variable_bins)[0] ({np.shape(out_digitized_variable_bins)[0]})!")
        # Extents matching:
        self.assertGreaterEqual(out_digitized_variable_bins[-1], out_binning_info.variable_extents[1], "out_digitized_variable_bins[-1] should be the maximum variable extent!") # Note assertGreaterEqual for fixed_bin_size mode
        self.assertEqual(out_digitized_variable_bins[0], out_binning_info.variable_extents[0], "out_digitized_variable_bins[0] should be the minimum variable extent!")
        self.assertGreaterEqual(active_position_extents[-1], out_binning_info.variable_extents[1], "active_position_extents[-1] should be the maximum variable extent!") # Note assertGreaterEqual for fixed_bin_size mode
        self.assertEqual(active_position_extents[0], out_binning_info.variable_extents[0], "active_position_extents[0] should be the minimum variable extent!")
        
        # Y position:
        active_position_extents = np.array([87.58388756, 153.31348421])
        out_digitized_variable_bins, out_binning_info = compute_spanning_bins(active_position_extents, bin_size=fixed_bin_size)
        print(f'test_compute_spanning_bins_bin_size_mode(): out_digitized_variable_bins: {out_digitized_variable_bins}, np.shape(out_digitized_variable_bins): {np.shape(out_digitized_variable_bins)}, out_binning_info: {out_binning_info}')
        self.assertEqual(out_binning_info.num_bins, np.shape(out_digitized_variable_bins)[0], f"out_binning_info.num_bins ({out_binning_info.num_bins}) must be equal to np.shape(out_digitized_variable_bins)[0] ({np.shape(out_digitized_variable_bins)[0]})!")
        # Extents matching:
        self.assertGreaterEqual(out_digitized_variable_bins[-1], out_binning_info.variable_extents[1], "out_digitized_variable_bins[-1] should be the maximum variable extent!") # Note assertGreaterEqual for fixed_bin_size mode
        self.assertEqual(out_digitized_variable_bins[0], out_binning_info.variable_extents[0], "out_digitized_variable_bins[0] should be the minimum variable extent!")
        self.assertGreaterEqual(active_position_extents[-1], out_binning_info.variable_extents[1], "active_position_extents[-1] should be the maximum variable extent!") # Note assertGreaterEqual for fixed_bin_size mode
        self.assertEqual(active_position_extents[0], out_binning_info.variable_extents[0], "active_position_extents[0] should be the minimum variable extent!")


    # def test_interleave_elements_string_elements(self):
    #     test_interleave_elements = {
    #         'string_elements': (['A','B','C','D'], ['a','b','c','d'], ['A', 'a', 'B', 'b', 'C', 'c', 'D', 'd']),
    #         'float_elements': ([0, 1, 2, 3], [1000,1001,1002,1003], [0, 1000, 1, 1001, 2, 1002, 3, 1003]),
    #         'nparrays': (np.array([0, 1, 2, 3]), np.array([1000,1001,1002,1003]), [0, 1000, 1, 1001, 2, 1002, 3, 1003]),
    #         'nparrays_transposed': (np.array([0, 1, 2, 3]).T, np.array([1000,1001,1002,1003]).T, [0, 1000, 1, 1001, 2, 1002, 3, 1003]),
    #         'points': (np.array([[0, 1, 2, 3], [0, 1, 2, 3]]).T, np.array([[1000,1001,1002,1003], [1000,1001,1002,1003]]).T, np.array([[   0,    0],
    #             [1000, 1000],
    #             [   1,    1],
    #             [1001, 1001],
    #             [   2,    2],
    #             [1002, 1002],
    #             [   3,    3],
    #             [1003, 1003]])),
    #     }
        
    #     a_starts = ['A','B','C','D']
    #     a_ends = ['a','b','c','d']
    #     a_interleaved = interleave_elements(a_starts, a_ends)
    #     print(f'a_interleaved: {a_interleaved}')
    #     self.assertListEqual(['A', 'a', 'B', 'b', 'C', 'c', 'D', 'd'], a_interleaved)
        
    # def test_interleave_elements_float_elements(self):        
    #     a_starts = [0, 1, 2, 3]
    #     a_ends = [1000,1001,1002,1003]
    #     a_interleaved = interleave_elements(a_starts, a_ends)
    #     print(f'a_interleaved: {a_interleaved}')
    #     self.assertListEqual([0, 1000, 1, 1001, 2, 1002, 3, 1003], a_interleaved)
        

    def test_interleave_elements_batch(self):        
        """ tests interleave_elements(...) """
        for test_name, test_tuple in self.test_interleave_elements.items():
            a_starts, a_ends, expected_interleaved_result = test_tuple
            print(f'test_name: {test_name}')
            a_interleaved_new = interleave_elements(a_starts, a_ends)
            print(f'\ta_interleaved_new: {a_interleaved_new}')
            self.assertSequenceEqual(np.array(expected_interleaved_result).tolist(), a_interleaved_new.tolist())
            
    def test_np_ffills(self):
        arr = np.array([[5, np.nan, np.nan, 7, 2],
                [3, np.nan, 1, 8, np.nan],
                [4, 9, 6, np.nan, np.nan]])
        
        """ 
        
        
        np.array([[5., 5., 5., 7., 2.],
       [3., 3., 1., 8., 8.],
       [4., 9., 6., 6., 6.]])
       
        
        np.array([[ 5.,  7.,  7.,  7.,  2.],
       [ 3.,  1.,  1.,  8., np.nan],
       [ 4.,  9.,  6., np.nan, np.nan]])
       
       
        """
        
        # np_ffill, np_ffill_1D, np_bfill_1D
        print(f'test_np_ffills(): arr: {arr}\n\tarr.shape: {arr.shape}, arr.ndim: {arr.ndim}')
        out = np_ffill_1D(arr, debug_print=True)
        print(f'np_ffill_1D: {out}')
        are_close = np.allclose(out,  np.array([[5., 5., 5., 7., 2.], [3., 3., 1., 8., 8.], [4., 9., 6., 6., 6.]]), equal_nan=True)
        print(f'\t are_close: {are_close}')
        self.assertTrue(are_close)
    #     self.assertSequenceEqual(out.tolist(), np.array([[5., 5., 5., 7., 2.],
    #    [3., 3., 1., 8., 8.],
    #    [4., 9., 6., 6., 6.]]).tolist()) # assertSequenceEqual doesn't work!!
        
        # out2 = np_ffill(arr, axis=1)
        # print(f'np_ffill axis=0: {out2}')
        # self.assertSequenceEqual(out.tolist(), out2.tolist())
    
        out2 = np_bfill_1D(arr)
        print(f'np_bfill_1D: {out2}')
        are_close2 = np.allclose(out2,  np.array([[ 5.,  7.,  7.,  7.,  2.], [ 3.,  1.,  1.,  8., np.nan], [ 4.,  9.,  6., np.nan, np.nan]]), equal_nan=True)
        print(f'\t are_close2: {are_close2}')
        self.assertTrue(are_close2)
        # self.assertSequenceEqual(out2.tolist(), np.array([[ 5.,  7.,  7.,  7.,  2.], [ 3.,  1.,  1.,  8., np.nan], [ 4.,  9.,  6., np.nan, np.nan]]).tolist()) # assertSequenceEqual doesn't work!!

    def test_np_ffills_1D(self):
        arr = np.array([5, np.nan, np.nan, 7, 2, 3, np.nan, 1, 8, np.nan, np.nan])
        arr = np.squeeze(arr) # make sure it's 1D
        print(f'test_np_ffills_1D(): arr: {arr}\n\tarr.shape: {arr.shape}, arr.ndim: {arr.ndim}')
        """ 
        
        
        np.array([[5., 5., 5., 7., 2.],
       [3., 3., 1., 8., 8.],
       [4., 9., 6., 6., 6.]])
       
        
        np.array([[ 5.,  7.,  7.,  7.,  2.],
       [ 3.,  1.,  1.,  8., np.nan],
       [ 4.,  9.,  6., np.nan, np.nan]])
       
       
        """
        
        # np_ffill, np_ffill_1D, np_bfill_1D
        out = np_ffill_1D(arr, debug_print=True)
        print(f'test_np_ffills_1D: {out}')
        are_close = np.allclose(out,  np.array([5., 5., 5., 7., 2., 3., 3., 1., 8., 8., 8.]), equal_nan=True)
        print(f'\t are_close: {are_close}')
        self.assertTrue(are_close)


if __name__ == '__main__':
    unittest.main()
    
    