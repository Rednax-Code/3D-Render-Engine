"""
Shapes
------

Defines the shapes for render3D.py
"""
import numpy as np
import numpy.typing as npt


class ShapeLike:
	pass

class cuboid(ShapeLike):
	triangles = (
		[0,3,7], [0,7,4],
		[4,7,6], [4,6,5],
		[5,6,2], [5,2,1],
		[1,2,3], [1,3,0],
		[3,2,6], [3,6,7],
		[5,1,0], [5,0,4]
		)
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

		unit_offsets = np.array([
			[-1,-1,-1],[-1,-1,1], [-1,1,1], [-1,1,-1],
			[1,-1,-1], [1,-1,1], [1,1,1], [1,1,-1]
		])

		self.position = position
		self.size = size
		self.offsets_center = position+(unit_offsets * size/2)