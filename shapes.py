"""
Shapes
------

Defines the shapes for render3D.

Could be used seperately, but i really can't immagine know why you would.

Features
--------
- plane
- cuboids
- ANY mesh (though larger meshes might change frames per second to seconds per frame)

Plans
-----
- Adding other basic shapes like tetrahedron, piramid, dodecahedron
- More support for .obj files
"""

import numpy as np
import numpy.typing as npt
import os
from vector_rotation import *


class ShapeLike:
	def __init__(self, position:npt.ArrayLike, rotation:npt.ArrayLike, size:npt.ArrayLike):
		self.position = np.array(position)
		self.rotation = np.array(rotation)
		self.size = np.array(size)

	def move(self, dx, dy, dz):
		"""
		I like to move it, move it!
		---------------------------
		"""

		d_vector = np.array([dx, dy, dz])
		self.position += d_vector
		self.offsets_center += d_vector

	def rotate(self, a, b, y):
		"""
		You spin me right round, baby right round
		-----------------------------------------
		"""

		offsets = self.offsets_center - self.position
		offsets = rotate_points(offsets, a, b, y)
		self.offsets_center = offsets + self.position
		self.rotation += np.array([a, b, y])


class plane(ShapeLike):
	triangles = (
		[0,1,2], [0,2,3]
	)
	def __init__(self, position:npt.ArrayLike, , rotation:npt.ArrayLike, size:npt.ArrayLike, texture):
		"""
		A plane! no... not the one that flies.

		Parameters
		----------
		position : `Array[x: float, y: float, z: float]`
			The starting position of your plane.
			
		size : `Array[width: float, height: float]`
			The starting size of the plane.
		
		texture : `Texture`
			The texture for the plane.

		Returns
		-------
		ShapeLike
		"""

		super(ShapeLike, self).__init__(position, rotation, size)

		self.size = np.array([self.size[0], 0, self.size[1]])

		unit_offsets = np.array([
			[-1,0,-1],[-1,0,1], [1,0,1], [1,0,-1]
		])

		self.position = position
		self.size = size
		self.offsets_center = position+(unit_offsets * size/2)


class cuboid(ShapeLike):
	triangles = (
		[0,3,7], [0,7,4],
		[4,7,6], [4,6,5],
		[5,6,2], [5,2,1],
		[1,2,3], [1,3,0],
		[3,2,6], [3,6,7],
		[5,1,0], [5,0,4]
	)
	def __init__(self, position:npt.ArrayLike, rotation:npt.ArrayLike, size:npt.ArrayLike, texture):
		"""
		Cube, box, 3D rectangle, whatever you wanna call it.

		Parameters
		----------
		position : `Array[x: float, y: float, z: float]`
			The starting position of the cuboid.
			
		size : `Array[width: float, height: float, depth: float]`
			The starting size of the cuboid.
		
		texture : `Texture`
			The texture for the cuboid.

		Returns
		-------
		ShapeLike
		"""

		super(ShapeLike, self).__init__(position, rotation, size)

		unit_offsets = np.array([
			[-1,-1,-1],[-1,-1,1], [-1,1,1], [-1,1,-1],
			[1,-1,-1], [1,-1,1], [1,1,1], [1,1,-1]
		])

		self.position = position
		self.size = size
		self.offsets_center = position+(unit_offsets * size/2)


class mesh(ShapeLike):
	def __init__(self, obj:os.PathLike, position:npt.ArrayLike, rotation:npt.ArrayLike, size:npt.ArrayLike, texture):
		"""
		A 3D mesh loaded from a .obj file

		Parameters
		----------
		obj : `os.path`
			The path to .obj file of your model.

		position : `Array[x: float, y: float, z: float]`
			The starting position of the object.
			
		size : `Array[width: float, height: float, depth: float]`
			The starting size of the object. (This scales all vertecies)
		
		texture : `Texture`
			The texture for the object.

		Returns
		-------
		ShapeLike
		"""

		super(ShapeLike, self).__init__(position, rotation, size)

		# Reading the obj file
		model = open(obj)
		offsets = []
		triangles = []
		for line in model.readlines():
			if line[0] == 'v':
				offsets.append(np.float_(line[2:-1].split(' ')))
			if line[0] == 'f':
				triangles.append(np.int_(line[2:-1].split(' '))-1)
		self.triangles = triangles

		# Centering offsets
		center = np.average(offsets, 0)
		offsets -= center

		self.position = position
		self.size = size
		self.offsets_center = position+(offsets * size/2)