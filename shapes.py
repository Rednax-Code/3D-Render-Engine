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

		self.position = position
		self.size = size
		self.offsets_center = position+(unit_offsets * size/2)




def rotate_x(points:npt.ArrayLike, y:float):
	return np.array([1,0,0,0,np.cos(y),-np.sin(y),0,np.sin(y),np.cos(y)]).reshape(3,3).dot(points.T).T

def rotate_y(points:npt.ArrayLike, b:float):
	return np.array([np.cos(b),0,np.sin(b),0,1,0,-np.sin(b),0,np.cos(b)]).reshape(3,3).dot(points.T).T

def rotate_z(points:npt.ArrayLike, a:float):
	return np.array([np.cos(a),-np.sin(a),0,np.sin(a),np.cos(a),0,0,0,1]).reshape(3,3).dot(points.T).T


class camerathing(ShapeLike):
	triangles = (
		[0,1,2], [0,1,3]
		)
	def __init__(self, position:npt.ArrayLike, texture):
		self.position = position
		self.rotation = np.array((0.0,0.0,0.0))
		self.fov = 90

		self.size = 500
		self.offsets_center = position+(np.array([[.0,.0,.0], [1.0,.0,.0], [.0,1.0,.0]]) * 500/2)

		self.default_plane_vectors = np.array([[1.0,.0,.0], [.0,1.0,.0]])
		self.plane_vectors = np.array([*self.default_plane_vectors])
		self.rotate(self.rotation)
	
	def rotate(self, rotation:npt.ArrayLike):
		self.rotation += rotation
		new_vectors = self.plane_vectors
		rotations = [rotate_x, rotate_y, rotate_z]
		axis = [i != 0 for i in rotation]
		for i in range(3):
			if axis[i]:
				new_vectors = rotations[i](new_vectors, rotation[i])
		self.plane_vectors = new_vectors
		
		self.plane_normal = np.cross(*self.plane_vectors)
		self.plane_normal /= np.linalg.norm(self.plane_normal)
		self.point = -self.plane_normal * (1000 / np.tan(self.fov/2))
		self.offsets_center = self.position+(np.array([[.0,.0,.0], self.plane_vectors[0], self.plane_vectors[1], self.point/250]) * 500/2)