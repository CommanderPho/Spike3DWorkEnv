from typing import Dict, List, Tuple, Optional, Callable, Union, Any
from typing_extensions import TypeAlias
import nptyping as ND
from nptyping import NDArray
import neuropy.utils.type_aliases as types

import numpy as np
import pandas as pd
from copy import deepcopy

import colorsys

class HeadingAngleHelpers:
	""" Help render a line where its local vertex color is given by the heading angle between that vertex's two adjacent segments. 

	from pyphocorehelpers.plotting.heading_angle_helpers import HeadingAngleHelpers
	
	"""
	# ==================================================================================================================================================================================================================================================================================== #
	# Heading Angles                                                                                                                                                                                                                                                                       #
	# ==================================================================================================================================================================================================================================================================================== #
	@classmethod
	def heading_angle_to_rainbow_rgba(cls, angle_deg: float, alpha: float = 1.0) -> Tuple[float, float, float, float]:
		"""Map heading angle in [0, 360) degrees to RGBA using ROYGBIV: 0°=red, 60°=yellow, 120°=green, 240°=blue, 300°=violet. Uses HSV with full saturation and value."""
		h = (float(angle_deg) % 360.0) / 360.0
		r, g, b = colorsys.hsv_to_rgb(h, 1.0, 1.0)
		return (float(r), float(g), float(b), float(alpha))


	@classmethod
	def heading_angles_to_rainbow_colors(cls, heading_angles_deg: NDArray, alpha: float = 1.0) -> NDArray:
		"""Convert array of heading angles (degrees, 0–360) to (N, 4) RGBA array using ROYGBIV mapping."""
		angles = np.asarray(heading_angles_deg, dtype=np.float64)
		h = (angles % 360.0) / 360.0
		N = len(h)
		rgb = np.array([colorsys.hsv_to_rgb(hi, 1.0, 1.0) for hi in h], dtype=np.float32)
		out = np.ones((N, 4), dtype=np.float32)
		out[:, :3] = rgb
		out[:, 3] = alpha
		return out


	@classmethod
	def headings_from_positions(cls, pos: NDArray) -> NDArray:
		"""Compute heading (direction of travel) in degrees [0, 360) at each vertex from (N, 2) positions. Segment i is from pos[i] to pos[i+1]; vertex i gets that segment's heading; last vertex gets previous segment's heading."""
		pos = np.asarray(pos, dtype=np.float64)
		if pos.shape[0] < 2:
			return np.full(max(1, pos.shape[0]), np.nan, dtype=np.float64)
		d = np.diff(pos, axis=0)
		angle_rad = np.arctan2(d[:, 1], d[:, 0])
		angle_deg = (np.degrees(angle_rad) + 360.0) % 360.0
		headings = np.empty(pos.shape[0], dtype=np.float64)
		headings[0] = angle_deg[0]
		headings[1:-1] = (angle_deg[:-1] + angle_deg[1:]) * 0.5
		headings[-1] = angle_deg[-1]
		return headings



	@classmethod
	def _heading_deg_to_compass_deg(cls, headings_deg):
		"""Convert atan2-style degrees (0=East) to compass (0=North)."""
		return (np.asarray(headings_deg, dtype=np.float64) - 90.0 + 360.0) % 360.0


	@classmethod
	def _positions_to_vertex_colors(cls, pos):
		"""Compute per-vertex colors from positions using heading (North=Red)."""
		headings_deg = cls.headings_from_positions(pos)
		compass_deg = cls._heading_deg_to_compass_deg(headings_deg)
		return cls.heading_angles_to_rainbow_colors(compass_deg, alpha=1.0)


