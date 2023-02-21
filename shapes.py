"""
Shapes
------

Defines the shapes for render3D.py
"""
import numpy as np
import numpy.typing as npt

unit_offsets = np.array([
	[-1,-1,-1],[-1,-1,1], [-1,1,1], [-1,1,-1],
	[1,-1,-1], [1,-1,1], [1,1,1], [1,1,-1]
])

class ShapeLike:
	pass

class cuboid(ShapeLike):
	def __init__(self, position:npt.ArrayLike, size:npt.ArrayLike, texture):
		"""
		Cube, box, 3D rectangle, whatever you wanna call it.

		Parameters
		----------
		position : Array[x: float, y: float, z: float]
			The starting position of the cuboid.
			
		size : Array[width: float, height: float, depth: float]
			The starting size of the cuboid.
		
		texture : Texture
			The texture for the cuboid.

		Returns
		-------
		ShapeLike
		"""

		position = np.array(position)
		size = np.array(size)

		self.position = position
		self.size = size
		self.offsets_center = position+(unit_offsets * size/2)