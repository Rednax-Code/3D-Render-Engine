import numpy as np
import numpy.typing as npt
from render3D.gpu_calculations import normalize
from render3D.vector_rotation import rotate_y

class camera_object:
	def __init__(self, position:npt.ArrayLike=[0,0,0], rotation:npt.ArrayLike=[.0,.0,.0], fov:float=90):
		"""
		The camera of your scene, which is created automatically by the engine.
	
		It can be accessed with: `render3D.camera`

		Parameters
		----------
		position : `Array[x: float, y: float, z: float]`
			The starting position of the camera.
			
		rotation : `Array[x: float, y: float, z: float]`
			The starting rotation of the camera around the axis x, y and z.
		
		fov : `float`
			The fov for the camera.

		Returns
		-------
		camera_object

		Issues
		------
		Rotating the camera round the z-axis might cause issues (untested)
		"""

		self.position = position # Is the offset of all objects relatively
		self.rotation = np.array(rotation)
		self.fov = fov

		self.default_plane_vectors = np.array([[1.0,.0,.0], [.0,1.0,.0]])
		self.plane_vectors = np.array([*self.default_plane_vectors])
		self.plane_normal = np.cross(*self.plane_vectors)
		self.plane_normal = normalize(self.plane_normal)
		self.point = -self.plane_normal * (1000 / np.tan(self.fov/2))
	
	def translate(self, translation:npt.ArrayLike) -> None:
		"""
		Moves the camera relative to is rotation around the y-axis

		Parameters
		----------
		translation : `Array[x: float, y: float, z: float]`
			The target position minus current position.

		Returns
		-------
		None
		"""
		self.position = self.position + rotate_y(np.array(translation), self.rotation[1])

	def rotate(self, rotation:npt.ArrayLike) -> None:
		"""
		Rotates the camera relatively to itself.

		So the x-axis changes depending on its current rotation around the y-axis.

		Parameters
		----------
		rotation : `Array[x: float, y: float, z: float]`
			The target rotation minus current rotation.

		Returns
		-------
		None
		"""
		self.rotation += rotation