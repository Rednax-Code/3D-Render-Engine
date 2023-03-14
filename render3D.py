"""
Render3D
--------

3D renderer originally created for pygame
"""
from pygame.math import *
import pygame.gfxdraw
import numpy as np
import numpy.typing as npt
import shapes
import lights
import time # temp


class camera_object:
	def __init__(self, position:npt.ArrayLike=[0,0,0], rotation:npt.ArrayLike=[.0,.0,.0], fov:float=90):
		self.position = position # Is the offset of all objects relatively
		self.rotation = np.array(rotation)
		self.fov = fov

		self.default_plane_vectors = np.array([[1.0,.0,.0], [.0,1.0,.0]])
		self.plane_vectors = np.array([*self.default_plane_vectors])
		self.plane_normal = np.cross(*self.plane_vectors)
		self.plane_normal /= np.linalg.norm(self.plane_normal)
		self.point = -self.plane_normal * (1000 / np.tan(self.fov/2))
	
	def translate(self, translation:npt.ArrayLike):
		self.position = self.position + rotate_y(np.array(translation), self.rotation[1])

	def rotate(self, rotation:npt.ArrayLike):
		self.rotation += rotation




camera: camera_object = None



def rotate_x(points:npt.ArrayLike, y:float):
	return np.array([1,0,0,0,np.cos(y),-np.sin(y),0,np.sin(y),np.cos(y)]).reshape(3,3).dot(points.T).T

def rotate_y(points:npt.ArrayLike, b:float):
	return np.array([np.cos(b),0,np.sin(b),0,1,0,-np.sin(b),0,np.cos(b)]).reshape(3,3).dot(points.T).T

def rotate_z(points:npt.ArrayLike, a:float):
	return np.array([np.cos(a),-np.sin(a),0,np.sin(a),np.cos(a),0,0,0,1]).reshape(3,3).dot(points.T).T

def rotate_points(points:npt.ArrayLike, a:float, b:float, y:float):
	return rotate_x(rotate_y(rotate_z(points, a), b), y)

def init(screen_size):
	"""
	Initializes the module and creates the camera object as render3D.camera
	"""
	global window_size
	window_size = screen_size

	global camera
	camera = camera_object()

	global objects_list
	objects_list = []


class scene:	
	def add_object(Object:shapes.ShapeLike):
		objects_list.append(Object)
	
	def add_objects(Objects:list[shapes.ShapeLike]):
		objects_list.extend(Objects)


def render(screen):
	#st = time.time() # timer

	# TEMPORARY
	light = [k for k in objects_list if isinstance(k, lights.LightLike)][0]
	light_direction = Vector3(list(light.direction))
	light_direction.rotate_rad_ip(-camera.rotation[0], np.cross([0,1,0], rotate_y(np.array([0,0,1]), camera.rotation[1])))
	light_direction.rotate_rad_ip(-camera.rotation[1], Vector3(0,1,0))
	light_direction = np.array(list(light_direction))

	render_objects = [i for i in objects_list if isinstance(i, shapes.ShapeLike)]
	for i in render_objects:
		cam_point = camera.point
		cam_normal = camera.plane_normal

		# World space >>> Camera translation space
		offsets = i.offsets_center - camera.position

		# Camera translation space >>> Camera rotation space
		# This works and i'm glad it does, but it's ugly af. Either don't touch it or spend 5 hours fixing it completely
		# render-time : 20%
		offsets -= cam_point
		new_offsets = []
		for j in offsets:
			vector = Vector3(list(j))
			vector.rotate_rad_ip(-camera.rotation[0], np.cross([0,1,0], rotate_y(np.array([0,0,1]), camera.rotation[1])))
			vector.rotate_rad_ip(-camera.rotation[1], Vector3(0,1,0))
			new_offsets.append(list(vector))
		offsets = np.array(new_offsets)
		offsets += cam_point

		# Camera rotation space >>> View space
		# Getting normal vectors and visible triangles
		# render-time : 30%
		normals = []
		for j in i.triangles:
			points = [offsets[j[k]] for k in (0,1,2)]
			line1, line2 = points[0:2] - points[2]
			normal = np.cross(line1, line2)
			normal /= np.linalg.norm(normal)
			normals.append(normal)
		
		# View space >>> Projection space
		t = np.dot(cam_normal, cam_point)/np.dot(cam_point - offsets, cam_normal)
		projection2D = cam_point + ((offsets - cam_point).T * t).T

		# Projectio space >>> Window space
		projection2D = np.array([0, window_size[1]]) + np.array([1, -1]) * projection2D[:, 0:2]
		projection2D = np.rint(projection2D + np.array([1, -1]) * np.array(window_size)/2)
		projection2D = projection2D.astype(int).tolist()

		
		# Drawing the triangles on screen
		# render-time : 10%-20%
		for j in range(len(i.triangles)):
			triangle = i.triangles[j]
			normal = normals[j]
			if np.dot(normal, offsets[triangle[2]]-cam_point) < 0:
				
				points = [projection2D[triangle[k]] for k in (0,1,2)]

				# Add lighting (TEMPORARY)
				color = np.array((255.0,255.0,255.0))
				color *= np.dot(normal, light_direction).clip(0, 1)
				
				pygame.gfxdraw.filled_polygon(screen, points, color)
				#pygame.gfxdraw.aapolygon(screen, points, (255,255,255)) # Could exchange this with "aatrigon()"
	
	#et = time.time() # timer
	#print((et - st)*1000, 'ms') # timer