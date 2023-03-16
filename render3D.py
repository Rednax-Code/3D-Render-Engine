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

	# Temp
	global selected_triangle
	selected_triangle = 0

	global objects_list
	objects_list = []

	global debug_font
	debug_font = pygame.font.SysFont('Arial', size=72)


class scene:
	def __init__(self):
		self.frames_since_start = 0
		self.render_time_total = 0

	def add_object(Object:shapes.ShapeLike):
		objects_list.append(Object)
	
	def add_objects(Objects:list[shapes.ShapeLike]):
		objects_list.extend(Objects)


def calc_normal(triangle):
	line1, line2 = triangle[0:2] - triangle[2]
	normal = np.cross(line1, line2)
	normal /= np.linalg.norm(normal)
	return normal


def render(screen, debug=False):
	st = time.time()
	
	# Gather camera information
	cam_position = camera.position
	cam_rotation = camera.rotation
	cam_point = camera.point
	cam_normal = camera.plane_normal

	# TEMPORARY
	light_objects = [i for i in objects_list if isinstance(i, lights.LightLike)]
	point_lights = []
	for i in light_objects:
		if isinstance(i, lights.ambient_light):
			light_color = np.array(i.color)
			ambient_lighting = i.intensity*light_color/255
		if isinstance(i, lights.directional_light):
			light_direction = Vector3(i.direction.tolist())
			light_direction.rotate_rad_ip(-cam_rotation[0], np.cross([0,1,0], rotate_y(np.array([0,0,1]), cam_rotation[1])))
			light_direction.rotate_rad_ip(-cam_rotation[1], Vector3(0,1,0))
			light_direction = np.array(light_direction)
			directional_lighting = i.intensity*np.array(i.color)/255
		if isinstance(i, lights.point_light):
			point_light_position = i.position - cam_position - cam_point
			new_point_light_position = []
			for j in point_light_position:
				vector = Vector3(j.tolist())
				vector.rotate_rad_ip(-cam_rotation[0], np.cross([0,1,0], rotate_y(np.array([0,0,1]), cam_rotation[1])))
				vector.rotate_rad_ip(-cam_rotation[1], Vector3(0,1,0))
				new_point_light_position.append(list(vector))
			point_light_position = np.array(new_point_light_position) + cam_point
			point_lighting = i.intensity*np.array(i.color)/255
			point_lights.append([point_light_position, point_lighting])


	# Gather render information
	# might want to give each object a render priority
	render_objects = [i for i in objects_list if isinstance(i, shapes.ShapeLike)]
	triangles = []
	offsets = []
	render_orders = []
	for i in render_objects:

		# Render order (not my favourite implementation)
		order = 0
		if isinstance(i, shapes.plane):
			order = -1

		triangles.extend(np.array(i.triangles)+len(offsets))
		offsets.extend(i.offsets_center)
		render_orders.extend([order for j in range(len(i.triangles))])
	
	# World space >>> Camera translation space
	offsets -= np.array(cam_position)

	# Camera translation space >>> Camera rotation space
	# This works and i'm glad it does, but it's ugly af. Either don't touch it or spend 5 hours fixing it completely
	# render-time : 20% outdated
	offsets -= cam_point
	new_offsets = []
	for j in offsets:
		vector = Vector3(j.tolist())
		vector.rotate_rad_ip(-cam_rotation[0], np.cross([0,1,0], rotate_y(np.array([0,0,1]), cam_rotation[1])))
		vector.rotate_rad_ip(-cam_rotation[1], Vector3(0,1,0))
		new_offsets.append(list(vector))
	offsets = np.array(new_offsets)
	offsets += cam_point

	# Camera rotation space >>> View space
	# Getting normal vectors, colors and visible triangles
	# render-time : 30% outdated
	visible_triangles = []
	normals = []
	colors = []
	render_orders_new = [] # Render order
	counter = 0
	for j in triangles:
		points = [offsets[j[k]] for k in (0,1,2)]
		normal = calc_normal(points)
		if np.dot(normal, offsets[j[2]]-cam_point) < 0:
			visible_triangles.append(points)
			normals.append(normal)
			colors.append((255,255,255))
			render_orders_new.append(render_orders[counter])
		counter += 1
	render_orders = render_orders_new
	triangle_count = len(visible_triangles)
	
	# Apply clipping
	remove_queue = []
	add_triangle_queue = []
	add_normal_queue = []
	add_color_queue = []
	add_render_order_queue = []
	clipping_distance = [.0,.0,300]
	for triangle in range(triangle_count):
		points = np.array(visible_triangles[triangle]) - cam_point - clipping_distance
		clips = [point for point in points if point[2] <= 0]
		non_clips = [point for point in points if point[2] > 0]

		if len(clips) > 0:
			# Remove triangles behind the camera
			remove_queue.append(triangle)

		if len(clips) == 1:
			# Devide triangle into 2 when 1 of it's points is behind the camera
			t = np.dot([.0,.0,1.0], clips[0])/np.dot(clips[0] - non_clips, [.0,.0,1.0])
			new_points = clips[0] + ((non_clips - clips[0]).T * t).T
			triangle_1 = [non_clips[1], non_clips[0], new_points[0]] + cam_point + clipping_distance
			triangle_2 = [new_points[1], non_clips[1], new_points[0]] + cam_point + clipping_distance
			add_triangle_queue.append(triangle_1)
			add_triangle_queue.append(triangle_2)
			add_normal_queue.extend((normals[triangle], normals[triangle]))
			if debug:
				add_color_queue.extend(((255,0,0), (0,255,0)))
			else:
				add_color_queue.extend((colors[triangle], colors[triangle]))
			add_render_order_queue.extend((render_orders[triangle], render_orders[triangle])) # Render order

		elif len(clips) == 2:
			# Replace triangle when 2 of it's points are behind the camera
			t = np.dot([.0,.0,1.0], non_clips[0])/np.dot(non_clips[0] - clips, [.0,.0,1.0])
			new_points = non_clips[0] + ((clips - non_clips[0]).T * t).T
			triangle_1 = [new_points[0], non_clips[0], new_points[1]] + cam_point + clipping_distance
			add_triangle_queue.append(triangle_1)
			add_normal_queue.append(normals[triangle])
			if debug:
				add_color_queue.append((0,0,255))
			else:
				add_color_queue.append(colors[triangle])
			add_render_order_queue.append(render_orders[triangle]) # Render order
	
	# Updating the triangle and normals lists after the clipping algorithm
	clipped_triangles = [visible_triangles[j] for j in range(triangle_count) if not j in remove_queue]
	normals = [normals[j] for j in range(triangle_count) if not j in remove_queue]
	colors = [colors[j] for j in range(triangle_count) if not j in remove_queue]
	render_orders = [render_orders[j] for j in range(triangle_count) if not j in remove_queue] # Render order
	clipped_triangles.extend(add_triangle_queue)
	normals.extend(add_normal_queue)
	colors.extend(add_color_queue)
	render_orders.extend(add_render_order_queue) # Render order
	triangle_count = len(clipped_triangles)

	# Sorting triangles - Render order (all of below)
	render_first_triangles, render_first_normals, render_first_colors = [], [], []
	to_sort_triangles, to_sort_normals, to_sort_colors = [], [], []
	for j in range(triangle_count):
		if render_orders[j] == -1:
			render_first_triangles.append(clipped_triangles[j])
			render_first_normals.append(normals[j])
			render_first_colors.append(colors[j])
		elif render_orders[j] == 0:
			to_sort_triangles.append(clipped_triangles[j])
			to_sort_normals.append(normals[j])
			to_sort_colors.append(colors[j])
	averages = [np.average(j, 0)[2] for j in to_sort_triangles]
	sorted_averages = sorted(averages, reverse=True)
	sort_order = []
	for j in sorted_averages:
		sort_order.append(averages.index(j))
		averages[averages.index(j)] = 0
	sorted_triangles = render_first_triangles + [to_sort_triangles[j] for j in sort_order]
	normals = render_first_normals + [to_sort_normals[j] for j in sort_order]
	colors = render_first_colors + [to_sort_colors[j] for j in sort_order]

	# View space >>> Projection space
	sorted_triangles = np.array(sorted_triangles)
	offsets = sorted_triangles.reshape([len(sorted_triangles)*3, 3])
	t = np.dot(cam_normal, cam_point)/np.dot(cam_point - offsets, cam_normal)
	projection2D = cam_point + ((offsets - cam_point).T * t).T

	# Projection space >>> Window space
	projection2D = np.array([0, window_size[1]]) + np.array([1, -1]) * projection2D[:, 0:2]
	projection2D = np.rint(projection2D + np.array([1, -1]) * np.array(window_size)/2)
	projection2D = projection2D.astype(int).tolist()
		
	# Drawing the triangles on screen
	# render-time : 10%-20% outdated
	for j in range(len(sorted_triangles)):

		# Get triangle information
		points = [projection2D[j*3+k] for k in (0,1,2)]
		normal = normals[j]
		color = colors[j]

		# Add ambient lighting
		ambient_color = ambient_lighting

		# Add directional lighting
		directional_color = directional_lighting * np.dot(normal/np.linalg.norm(normal), -light_direction/np.linalg.norm(light_direction)).clip(0, 1)

		# Add point lighting
		point_color = (0,0,0)
		center = np.average(sorted_triangles[j], 0)
		for k in point_lights:
			point_light_position = k[0]
			point_lighting = k[1]
			light_direction = center - point_light_position
			point_color += point_lighting * np.dot(normal/np.linalg.norm(normal), -light_direction/np.linalg.norm(light_direction)).clip(0, 1)

		# Calculate total color
		total_color = (ambient_color+directional_color+point_color)/255
		total_color *= color

		# Draw the triangle on screen
		pygame.gfxdraw.filled_polygon(screen, points, total_color)
		pygame.gfxdraw.aapolygon(screen, points, (255,255,255)) # Could exchange this with "aatrigon()"
	
	#frames_since_start = frames_since_start + 1
	scene.frames_since_start
	et = time.time()
	render_time = (et-st)*1000, 1
	scene.render_time_total += render_time
	render_time_average = scene.render_time_total / scene.frames_since_start

	# Draw debug screen
	if debug:
		render_time_text = debug_font.render(str(round(render_time))+' ms', True, (255,255,255))
		render_time_average_text = debug_font.render(str(render_time_average)+' ms', True, (255,255,255))
		screen.blit(render_time_text, [50, 50])

	return render_time