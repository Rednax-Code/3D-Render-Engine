"""
Render3D
--------

3D renderer originally created for pygame
"""
from pygame.math import *
import numpy as np
import numpy.typing as npt
import shapes


class camera_object:
	def __init__(self, position:npt.ArrayLike=[0,0,0], rotation:npt.ArrayLike=[.0,.0,.0], fov:float=90):
		self.position = position # Is the offset of all objects relatively
		self.rotation = np.array(rotation)
		self.fov = fov

		self.default_plane_vectors = np.array([[1.0,.0,.0], [.0,1.0,.0]])
		#self.default_point = -np.cross(*self.default_plane_vectors) * (1000 / np.tan(fov))
		self.plane_vectors = np.array([*self.default_plane_vectors])
		self.rotate(rotation)
	
	def translate(self, translation:npt.ArrayLike):
		self.position = self.position + rotate_y(np.array(translation), self.rotation[2])

	def rotate(self, rotation:npt.ArrayLike):
		self.rotation += np.array([rotation[-i] for i in range(3)])
		print(self.rotation)
		new_vectors = self.plane_vectors
		rotations = [rotate_x, rotate_y, rotate_z]
		axis = [i != 0 for i in rotation]
		for i in range(3):
			if axis[-i]:
				new_vectors = rotations[-i](new_vectors, rotation[-i])
		self.plane_vectors = new_vectors
		self.plane_normal = np.cross(*self.plane_vectors)
		self.plane_normal /= np.linalg.norm(self.plane_normal)
		self.point = -self.plane_normal * (1000 / np.tan(self.fov/2))




camera: camera_object = None



def rotate_x(points:npt.ArrayLike, y:float):
	return np.array([1,0,0,0,np.cos(y),-np.sin(y),0,np.sin(y),np.cos(y)]).reshape(3,3).dot(points.T).T

def rotate_y(points:npt.ArrayLike, b:float):
	return np.array([np.cos(b),0,np.sin(b),0,1,0,-np.sin(b),0,np.cos(b)]).reshape(3,3).dot(points.T).T

def rotate_z(points:npt.ArrayLike, a:float):
	return np.array([np.cos(a),-np.sin(a),0,np.sin(a),np.cos(a),0,0,0,1]).reshape(3,3).dot(points.T).T

def rotate_points(points:npt.ArrayLike, a:float, b:float, y:float):
	return rotate_x(rotate_y(rotate_z(points, a), b), y)



def init():
	"""
	Initializes the module and creates the camera object as render3D.camera
	"""
	global camera
	camera = camera_object()


def render(objects:list[shapes.ShapeLike]):
	projections = []
	for i in objects:
		cam_point = camera.point
		cam_normal = camera.plane_normal
		offsets = i.offsets_center - camera.position

		t = np.dot(cam_normal, cam_point)/np.dot(cam_point - offsets, cam_normal)
		projection2D = cam_point + ((offsets - cam_point).T * t).T
		#if not camera.rotation.all(0):
		#	projection2D = rotate_points(projection2D, *-camera.rotation)
		projection2D = rotate_x(projection2D, -camera.rotation[0])
		projection2D = rotate_y(projection2D, -camera.rotation[2])
		projection2D = rotate_z(projection2D, -camera.rotation[1])

		projection2D = np.rint(projection2D[:, 0:2]) + np.array([1920, 1080])/2
		projection2D = projection2D.astype(int).tolist()
		
		projections.append(projection2D)
		
	return projections