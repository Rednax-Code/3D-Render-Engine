"""
Render3D
--------

A 3D renderer originally created for pygame.

I started on this project around the start of march 2023.
What i plan to do with it all... idk, BUT it's great fun.
It is currently VERY slow (cus it's python), but i'll probably add some Cython magic.

Features
--------
- Load in .obj files.
- Render triangle meshes and some basic shapes like cubes and planes.
- Doesn't render triangles facing away from the camera.
- Clip triangles with points in/behind camera.
- Painter-style depth mapping.
- Camera object which can move and rotate.
- Lighting with ambient, directional and point lights.

Plans
-----
- Optimilization through Cython
- Texturing
- perhaps smooth lighting shaders?
- shadows?!
"""

from pygame.math import *
from pygame import Surface
import pygame.gfxdraw
import numpy as np
import numpy.typing as npt
import shapes
import lights
from vector_rotation import *
import time # timer


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
		self.plane_normal /= np.linalg.norm(self.plane_normal)
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




camera: camera_object




def init(screen_size):
	"""
	Initializes the module and creates the camera object as `render3D.camera`

	Parameters
	----------
	screen_size : `Array[x: int, y: int]`
		Sets the size of the screen.

	Returns
	-------
	None
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
	def add_object(Object:shapes.ShapeLike):
		objects_list.append(Object)
	
	def add_objects(Objects:list[shapes.ShapeLike]):
		objects_list.extend(Objects)


def calc_normal(triangle):
	line1, line2 = triangle[0:2] - triangle[2]
	normal = np.cross(line1, line2)
	normal /= (normal[0]**2+normal[1]**2+normal[2]**2)**.5
	return normal


def render(screen:Surface, debug=False) -> float:
	"""
	The BIG function to `magically` draw all your objects on the screen.

	Parameters
	----------
	screen : `pygame.Surface`
		The pygame display surface object.
	
	debug : `bool`, optional
		This will enable the debug menu showing render time on-screen and colors clipped triangles.

	Returns
	-------
	float
		The time it took to render the image.
	"""

	timer_start = time.time()
	
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

	timer_render_setup = time.time()
	
	# World space >>> Camera translation space
	offsets -= np.array(cam_position)

	# Camera translation space >>> Camera rotation space
	# I don't know why or how this works, sooo i'm just not gonna touch it.
	offsets -= cam_point
	offsets = rotate_around_vector(offsets, np.cross([0,1,0], rotate_y(np.array([0,0,1]), cam_rotation[1])), -cam_rotation[0])
	offsets = rotate_around_vector(offsets, Vector3(0,1,0), -cam_rotation[1]) 
	offsets += cam_point

	timer_rotation_space = time.time()

	# Camera rotation space >>> View space
	# Getting normal vectors, colors and visible triangles
	visible_triangles = []
	normals = []
	colors = []
	render_orders_new = [] # Render order
	counter = 0

	triangle_points = np.array(offsets[triangles])

	for j in range(len(triangles)):
		points = np.array(triangle_points[j])
		normal = calc_normal(points)
		if np.dot(normal, points[2]-cam_point) < 0:
			visible_triangles.append(points)
			normals.append(normal)
			colors.append((255,255,255))
			render_orders_new.append(render_orders[counter])
		counter += 1

	"""
	triangle_points = []
	triangle_normals = []
	for j in range(len(triangles)):
		triangle_points.append(np.array(offsets[triangles[j][0:3]]))
		triangle_normals.append(calc_normal(triangle_points[j]))
	for j in range(len(triangle_points)):
		if np.dot(triangle_normals[j], triangle_points[j][2]-cam_point) < 0:
			visible_triangles.append(triangle_points[j])
			normals.append(triangle_normals[j])
			colors.append((255,255,255))
			render_orders_new.append(render_orders[counter])
		counter += 1
	"""
	render_orders = list(render_orders_new)
	triangle_count = len(visible_triangles)
	
	timer_view_space = time.time()
	
	# Apply clipping
	remove_queue = []
	add_triangle_queue = []
	add_normal_queue = []
	add_color_queue = []
	add_render_order_queue = []
	clipping_distance = [.0,.0,150]
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

	timer_clipped = time.time()

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

	timer_sorted = time.time()

	# View space >>> Projection space
	sorted_triangles = np.array(sorted_triangles)
	offsets = sorted_triangles.reshape([len(sorted_triangles)*3, 3])
	t = np.dot(cam_normal, cam_point)/np.dot(cam_point - offsets, cam_normal)
	projection2D = cam_point + ((offsets - cam_point).T * t).T

	# Projection space >>> Window space
	projection2D = np.array([0, window_size[1]]) + np.array([1, -1]) * projection2D[:, 0:2]
	projection2D = np.rint(projection2D + np.array([1, -1]) * np.array(window_size)/2)
	projection2D = projection2D.astype(int).tolist()

	timer_projected = time.time()
		
	# Drawing the triangles on screen
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
		if debug:
			pygame.gfxdraw.aapolygon(screen, points, (255,255,255)) # Could exchange this with "aatrigon()"
	

	timer_end = time.time()
	render_time = (timer_end-timer_start)*1000
	setup_time = (timer_render_setup-timer_start)*1000
	world_to_rotation_time = (timer_rotation_space-timer_render_setup)*1000
	rotation_to_view_time = (timer_view_space-timer_rotation_space)*1000
	view_to_clipped_time = (timer_clipped-timer_view_space)*1000
	clipped_to_sorted_time = (timer_sorted-timer_clipped)*1000
	sorted_to_projected_time = (timer_projected-timer_sorted)*1000
	projected_to_drawn_time = (timer_end-timer_projected)*1000

	# Draw debug screen
	if debug:
		render_text = debug_font.render('Total frame: '+str(round(render_time,1))+' ms', True, (255,255,255))
		setup_text = debug_font.render('Render Setup: '+str(round(setup_time,1))+' ms', True, (255,255,255))
		world_to_rotation_text = debug_font.render('World to Rotation Space: '+str(round(world_to_rotation_time,1))+' ms', True, (255,255,255))
		rotation_to_view_text = debug_font.render('Rotation to View Space: '+str(round(rotation_to_view_time,1))+' ms', True, (255,255,255))
		view_to_clipped_text = debug_font.render('View Space to Clipped: '+str(round(view_to_clipped_time,1))+' ms', True, (255,255,255))
		clipped_to_sorted_text = debug_font.render('Clipped to Sorted: '+str(round(clipped_to_sorted_time,1))+' ms', True, (255,255,255))
		sorted_to_projected_text = debug_font.render('Sorted to Projected: '+str(round(sorted_to_projected_time,1))+' ms', True, (255,255,255))
		projected_to_drawn_text = debug_font.render('Projected to Drawn: '+str(round(projected_to_drawn_time,1))+' ms', True, (255,255,255))

		screen.blit(render_text, [50, 50])
		screen.blit(setup_text, [50, 120])
		screen.blit(world_to_rotation_text, [50, 190])
		screen.blit(rotation_to_view_text, [50,260])
		screen.blit(view_to_clipped_text, [50,330])
		screen.blit(clipped_to_sorted_text, [50,400])
		screen.blit(sorted_to_projected_text, [50,470])
		screen.blit(projected_to_drawn_text, [50,540])

	return render_time