import unittest
import numpy as np
import pandas as pd
from unittest.mock import patch
import pytest
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
	from pyphocorehelpers.assertion_helpers import Assert


def random_array():
    choices = [1, 2, 3, 4, 5, 6, 7, 8, 9, np.nan]
    out = np.random.choice(choices, size=(1000, 10))
    return out


class TestAssertionHelpers(unittest.TestCase):
    
    def test_shape_equals_numpy_array(self):
        """Test shape_equals with numpy arrays of correct shape."""
        test_array = np.zeros((3, 4))
        # This should not raise an exception
        try:
            Assert.shape_equals(test_array, (3, 4))
        except AssertionError:
            self.fail("Assert.shape_equals raised AssertionError unexpectedly!")
        
    def test_shape_equals_list(self):
        """Test shape_equals with lists."""
        test_list = [[1, 2, 3], [4, 5, 6]]
        # This should not raise an exception
        try:
            Assert.shape_equals(test_list, (2, 3))
        except AssertionError:
            self.fail("Assert.shape_equals raised AssertionError unexpectedly!")
        
    def test_shape_equals_failure(self):
        """Test shape_equals raises assertion error with incorrect shape."""
        test_array = np.zeros((3, 4))
        with self.assertRaises(AssertionError) as context:
            Assert.shape_equals(test_array, (4, 3))
        self.assertIn("must be of length", str(context.exception))
        
    def test_shape_equals_single_dimension(self):
        """Test shape_equals with a single dimension."""
        test_array = np.zeros(5)
        # This should not raise an exception
        try:
            Assert.shape_equals(test_array, (5,))
        except AssertionError:
            self.fail("Assert.shape_equals raised AssertionError unexpectedly!")
        
    def test_same_shape_numpy_arrays(self):
        """Test same_shape with multiple numpy arrays of the same shape."""
        array1 = np.zeros((2, 3))
        array2 = np.ones((2, 3))
        array3 = np.full((2, 3), 2)
        # This should not raise an exception
        try:
            Assert.same_shape(array1, array2, array3)
        except AssertionError:
            self.fail("Assert.same_shape raised AssertionError unexpectedly!")
        
    def test_same_shape_mixed_types(self):
        """Test same_shape with mixed types that have the same shape."""
        array1 = np.zeros((2, 3))
        list1 = [[1, 2, 3], [4, 5, 6]]
        # This should not raise an exception
        try:
            Assert.same_shape(array1, list1)
        except AssertionError:
            self.fail("Assert.same_shape raised AssertionError unexpectedly!")
        
    def test_same_shape_failure(self):
        """Test same_shape raises assertion error with different shapes."""
        array1 = np.zeros((2, 3))
        array2 = np.ones((3, 2))
        with self.assertRaises(AssertionError) as context:
            Assert.same_shape(array1, array2)
        self.assertIn("must be of shape", str(context.exception))
        
    def test_same_shape_single_array(self):
        """Test same_shape with a single array."""
        array1 = np.zeros((2, 3))
        # This should not raise an exception
        try:
            Assert.same_shape(array1)
        except AssertionError:
            self.fail("Assert.same_shape raised AssertionError unexpectedly!")
        
    def test_same_shape_empty_args(self):
        """Test same_shape with no arguments."""
        # This should not raise an exception
        try:
            Assert.same_shape()
        except AssertionError:
            self.fail("Assert.same_shape raised AssertionError unexpectedly!")
        
    @patch('inspect.currentframe')
    def test_variable_name_extraction(self, mock_currentframe):
        """Test that variable names are correctly extracted."""
        # Mock the frame and its locals
        mock_frame = unittest.mock.MagicMock()
        mock_currentframe.return_value.f_back = mock_frame
        
        # Create a test array
        test_array = np.zeros((2, 3))
        
        # Set up the mock locals to include our test array with a specific name
        mock_frame.f_locals = {'my_test_array': test_array}
        
        # This should raise an exception with the correct variable name
        with self.assertRaises(AssertionError) as context:
            Assert.shape_equals(test_array, (3, 2))
        self.assertIn("my_test_array must be of length", str(context.exception))
        
    def test_same_shape_with_pandas(self):
        """Test same_shape with pandas DataFrames."""
        df1 = pd.DataFrame(np.zeros((3, 4)))
        df2 = pd.DataFrame(np.ones((3, 4)))
        # This should not raise an exception
        try:
            Assert.same_shape(df1, df2)
        except AssertionError:
            self.fail("Assert.same_shape raised AssertionError unexpectedly!")
        
    def test_same_shape_with_different_pandas(self):
        """Test same_shape raises assertion error with different shaped DataFrames."""
        df1 = pd.DataFrame(np.zeros((3, 4)))
        df2 = pd.DataFrame(np.ones((4, 3)))
        with self.assertRaises(AssertionError) as context:
            Assert.same_shape(df1, df2)
        self.assertIn("must be of shape", str(context.exception))

    def test_shape_equals_error_message_content(self):
        """Test that shape_equals error message contains the actual shape."""
        test_array = np.zeros((3, 4))
        with self.assertRaises(AssertionError) as context:
            Assert.shape_equals(test_array, (4, 3))
        error_message = str(context.exception)
        self.assertIn("(3, 4)", error_message)  # Should contain the actual shape
        self.assertIn("(4, 3)", error_message)  # Should contain the expected shape

    def test_same_shape_error_message_content(self):
        """Test that same_shape error message contains all shapes."""
        array1 = np.zeros((2, 3))
        array2 = np.ones((3, 2))
        with self.assertRaises(AssertionError) as context:
            Assert.same_shape(array1, array2)
        error_message = str(context.exception)
        self.assertIn("(2, 3)", error_message)  # Should contain the reference shape
        self.assertIn("(3, 2)", error_message)  # Should contain the mismatched shape


if __name__ == '__main__':
    unittest.main()
