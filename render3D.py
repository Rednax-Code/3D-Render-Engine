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
	def __init__(self, position:npt.ArrayLike=[0,0,0], fov:float=90):
		self.position = position # Is center of plane
		self.fov = fov

		pv_1 = [1,0,0]
		pv_2 = [0,1,0]
		self.plane_normal = np.cross(pv_1, pv_2)
		self.point = -self.plane_normal * (1000 / np.tan(fov))


camera: camera_object = None

def init():
	"""
	Initializes the module and creates the camera object as render3D.camera
	"""
	global camera
	camera = camera_object()


def render(objects:list[shapes.ShapeLike]):
	for i in objects:
		offsets = i.offsets_center - camera.position
		pass