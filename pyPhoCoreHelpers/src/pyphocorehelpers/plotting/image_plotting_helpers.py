from matplotlib import pyplot as plt

class IMShowHelpers:
	""" Helpers related to matplotlib's `imshow(...)` command which have tons of ideosyncracies, especially related to the origin
	
	from pyphocorehelpers.plotting.image_plotting_helpers import IMShowHelpers
	
	"""
	# ==================================================================================================================== #
	# Vertical (x == vertical axis) plot                                                                                   #
	# ==================================================================================================================== #
	# The simple goal is to be able to plot a heatmap, for example one obtained from a 2D histogram of x and y data, and plot it with relevant points overlaying it.
	@classmethod
	def final_x_vertical_plot_imshow(cls, xbin_edges, ybin_edges, matrix, ax=None):
		""" Plots the matrix data in the 'x == vertical orientation'
		
		fig, ax, im_out = good_plot_imshow(xbin, ybin, matrix) """
		def setup_stable_axes_limits(xbins_edges, ybin_edges, ax):
			" manually sets the axis data limits to disable autoscaling given the xbins_edges/ybin_edges "
			# x == vertical orientation:
			ax.set_xlim(left=ybin_edges[0], right=ybin_edges[-1])
			ax.set_ylim(bottom=xbins_edges[0], top=xbins_edges[-1])
			# x == horizontal orientation:
			# ax.set_xlim(left=xbins_edges[0], right=xbins_edges[-1])
			# ax.set_ylim(bottom=ybin_edges[0], top=ybin_edges[-1])

		if ax is None:
			fig, axs = plt.subplots(ncols=1, nrows=1, figsize=(15,15), clear=True)
			ax = axs
		else:
			fig = ax.get_figure()
			
		variable_value = matrix
		
		xmin, xmax, ymin, ymax = (xbin_edges[0], xbin_edges[-1], ybin_edges[0], ybin_edges[-1])
		y_first_extent = (ymin, ymax, xmin, xmax) # swapped the order of the extent axes.
		main_plot_kwargs = {
			'cmap': 'viridis',
			'origin':'lower',
			'extent':y_first_extent,
		}
		
		"""
		Note that changing the origin while keeping everything else the same doesn't flip the direction of the yaxis labels despite flipping the yaxis of the data.
		"""
		im_out = ax.imshow(variable_value, **main_plot_kwargs)
		ax.set_title(f'origin=lower \nextent=(ymin, ymax, xmin, xmax): {y_first_extent}')
		# Note that the xlabel and ylabel commands are for the opposite axis!
		ax.set_xlabel('y')
		ax.set_ylabel('x')
		setup_stable_axes_limits(xbin_edges, ybin_edges, ax)
		return fig, ax, im_out

	@classmethod
	def final_x_vertical_add_point(cls, test_point_x_y, ax):
		""" Plots the data point/points in the 'x == vertical orientation':
		line = good_add_point(test_point, test_point[0], ax) """
		line, = ax.plot(test_point_x_y[1], test_point_x_y[0], marker='d', markersize=40.0, linestyle='None', color='red', alpha=0.5)
		return line


	# ==================================================================================================================== #
	# Horizontal (x == horizontal axis) plot                                                                               #
	# ==================================================================================================================== #
	# Attempt to convert data to typical x == horizontal axis plot:
	@classmethod
	def final_x_horizontal_plot_imshow(cls, xbin_edges, ybin_edges, matrix, ax=None):
		""" Plots the matrix data in the 'x == horizontal orientation'
		fig, ax, im_out = final_x_horizontal_plot_imshow(xbin, ybin, matrix) """
		def setup_stable_axes_limits(xbins_edges, ybin_edges, ax):
			" manually sets the axis data limits to disable autoscaling given the xbins_edges/ybin_edges "
			# x == horizontal orientation:
			ax.set_xlim(left=xbins_edges[0], right=xbins_edges[-1])
			ax.set_ylim(bottom=ybin_edges[0], top=ybin_edges[-1])

		if ax is None:
			fig, axs = plt.subplots(ncols=1, nrows=1, figsize=(15,15), clear=True)
			ax = axs
		else:
			fig = ax.get_figure()
			
		variable_value = matrix
		
		xmin, xmax, ymin, ymax = (xbin_edges[0], xbin_edges[-1], ybin_edges[0], ybin_edges[-1]) # the same for both orientations
		x_first_extent = (xmin, xmax, ymin, ymax) # traditional order of the extant axes
		# y_first_extent = (ymin, ymax, xmin, xmax) # swapped the order of the extent axes.
		main_plot_kwargs = {
			'cmap': 'viridis',
			'origin':'lower',
			'extent':x_first_extent,
		}
		
		"""
		Note that changing the origin while keeping everything else the same doesn't flip the direction of the yaxis labels despite flipping the yaxis of the data.
		"""
		im_out = ax.imshow(variable_value, **main_plot_kwargs)
		# ax.set_title(f'origin=lower \nextent=(ymin, ymax, xmin, xmax): {y_first_extent}')
		# Note that the xlabel and ylabel commands are for the opposite axis!
		ax.set_xlabel('x')
		ax.set_ylabel('y')
		setup_stable_axes_limits(xbin_edges, ybin_edges, ax)
		return fig, ax, im_out

	@classmethod
	def final_x_horizontal_add_point(cls, test_point_x_y, ax):
		""" Plots the data point/points in the 'x == horizontal orientation':
		line = final_x_horizontal_add_point(test_point, test_point[0], ax) """
		line, = ax.plot(test_point_x_y[0], test_point_x_y[1], marker='d', markersize=40.0, linestyle='None', color='red', alpha=0.5)
		return line


