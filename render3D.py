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
import time # timer


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


def calc_normal(triangle):
	line1, line2 = triangle[0:2] - triangle[2]
	normal = np.cross(line1, line2)
	normal /= np.linalg.norm(normal)
	return normal


def render(screen):
	#st = time.time() # timer

	# TEMPORARY
	light_objects = [i for i in objects_list if isinstance(i, lights.LightLike)]
	for i in light_objects:
		if isinstance(i, lights.ambient_light):
			light_color = np.array(i.color)
			ambient_lighting = i.intensity*light_color/255
		if isinstance(i, lights.directional_light):
			light_direction = Vector3(i.direction.tolist())
			light_direction.rotate_rad_ip(-camera.rotation[0], np.cross([0,1,0], rotate_y(np.array([0,0,1]), camera.rotation[1])))
			light_direction.rotate_rad_ip(-camera.rotation[1], Vector3(0,1,0))
			light_direction = np.array(light_direction)



	render_objects = [i for i in objects_list if isinstance(i, shapes.ShapeLike)]
	for i in render_objects:
		cam_point = camera.point
		cam_normal = camera.plane_normal

		# World space >>> Camera translation space
		offsets = i.offsets_center - camera.position

		# Camera translation space >>> Camera rotation space
		# This works and i'm glad it does, but it's ugly af. Either don't touch it or spend 5 hours fixing it completely
		# render-time : 20% outdated
		offsets -= cam_point
		new_offsets = []
		for j in offsets:
			vector = Vector3(j.tolist())
			vector.rotate_rad_ip(-camera.rotation[0], np.cross([0,1,0], rotate_y(np.array([0,0,1]), camera.rotation[1])))
			vector.rotate_rad_ip(-camera.rotation[1], Vector3(0,1,0))
			new_offsets.append(list(vector))
		offsets = np.array(new_offsets)
		offsets += cam_point

		# Camera rotation space >>> View space
		# Getting normal vectors and visible triangles
		# render-time : 30% outdated
		normals = []
		visible_triangles = []
		for j in i.triangles:
			points = [offsets[j[k]] for k in (0,1,2)]
			normal = calc_normal(points)
			if np.dot(normal, offsets[j[2]]-cam_point) < 0:
				visible_triangles.append(points)
				normals.append(normal)
		
		# Apply clipping
		remove_queue = []
		add_triangle_queue = []
		add_normal_queue = []
		for triangle in range(len(visible_triangles)):
			points = np.array(visible_triangles[triangle]) - camera.point - [.0,.0,100]
			clips = [point for point in points if point[2] <= 0]
			non_clips = [point for point in points if point[2] > 0]

			if len(clips) > 0:
				# Remove triangles behind the camera
				remove_queue.append(triangle)

			if len(clips) == 1:
				# Devide triangle into 2 when 1 of it's points is behind the camera
				t = np.dot([.0,.0,1.0], clips[0])/np.dot(clips[0] - non_clips, [.0,.0,1.0])
				new_points = clips[0] + ((non_clips - clips[0]).T * t).T
				triangle_1 = [non_clips[1], non_clips[0], new_points[0]] + camera.point + [.0,.0,100]
				triangle_2 = [new_points[1], non_clips[1], new_points[0]] + camera.point + [.0,.0,100]
				add_triangle_queue.append(triangle_1)
				add_normal_queue.append(normals[triangle])
				add_triangle_queue.append(triangle_2)
				add_normal_queue.append(normals[triangle])

			elif len(clips) == 2:
				# Replace triangle when 2 of it's points are behind the camera
				t = np.dot([.0,.0,1.0], non_clips[0])/np.dot(non_clips[0] - clips, [.0,.0,1.0])
				new_points = non_clips[0] + ((clips - non_clips[0]).T * t).T
				triangle_1 = [new_points[0], non_clips[0], new_points[1]] + camera.point + [.0,.0,100]
				add_triangle_queue.append(triangle_1)
				add_normal_queue.append(normals[triangle])
		
		# Updating the triangle and normals lists after the clipping algorithm
		clipped_triangles = [visible_triangles[j] for j in range(len(visible_triangles)) if not j in remove_queue]
		normals = [normals[j] for j in range(len(visible_triangles)) if not j in remove_queue]
		clipped_triangles.extend(add_triangle_queue)
		normals.extend(add_normal_queue)

		# View space >>> Projection space
		clipped_triangles = np.array(clipped_triangles)
		offsets = clipped_triangles.reshape([len(clipped_triangles)*3, 3])
		t = np.dot(cam_normal, cam_point)/np.dot(cam_point - offsets, cam_normal)
		projection2D = cam_point + ((offsets - cam_point).T * t).T

		# Projection space >>> Window space
		projection2D = np.array([0, window_size[1]]) + np.array([1, -1]) * projection2D[:, 0:2]
		projection2D = np.rint(projection2D + np.array([1, -1]) * np.array(window_size)/2)
		projection2D = projection2D.astype(int).tolist()

		# Sorting triangles
		clipped_triangles = sorted(clipped_triangles, key=lambda x: np.average(x, 1)[2], reverse=True) # if needed reverse
		
		# Drawing the triangles on screen
		# render-time : 10%-20% outdated
		for j in range(len(clipped_triangles)):
			normal = normals[j]
			points = [projection2D[j*3+k] for k in (0,1,2)]

			# Add lighting (TEMPORARY)
			color = np.array((200.0,200.0,200.0))
			color *= np.dot(normal, light_direction).clip(0, 1)
				
			pygame.gfxdraw.filled_polygon(screen, points, ambient_lighting+color)
			#pygame.gfxdraw.aapolygon(screen, points, (255,255,255)) # Could exchange this with "aatrigon()"
	
	#et = time.time() # timer
	#print((et - st)*1000, 'ms') # timer