import pygame
import pygame.gfxdraw
from pygame.locals import *
from pygame.math import *
import render3D
import os.path
import numpy as np


# Initializing window
pygame.init()
display_info = pygame.display.Info()
width, height = display_info.current_w, display_info.current_h
flags = pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.FULLSCREEN
screen = pygame.display.set_mode((width, height), flags, vsync=1)
pygame.display.set_caption("3D")
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)


# Initializing renderer
render3D.init([width, height])

# Loading in triangle meshes
shape = os.path.join(os.path.dirname(__file__),'objects\\house.obj')

# Adding first shapes
render3D.scene.add_objects([
	render3D.shapes.plane([0,-525,0], [5000,5000], None),
	render3D.shapes.mesh(shape, [-700,0,1000], [500,500,500], None),
	render3D.shapes.mesh(shape, [700,0,1000], [500,500,500], None),
	render3D.lights.ambient_light(20, [255,255,255]),
	render3D.lights.directional_light([1,-1,1], 100, [255,255,255])
])

# Camera movement speed
Speed = 1
pygame.mouse.get_rel()

# Key input handler
input_list = [K_w, K_s, K_a, K_d, K_LSHIFT, K_SPACE, K_e, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_RCTRL, K_RSHIFT, K_i, K_k, K_j, K_l, K_u, K_o]
inputs = {}
for i in input_list:
	inputs[i] = False
inputs_camera_move = {K_w: [0,0,5], K_s: [0,0,-5], K_a: [-5,0,0], K_d: [5,0,0], K_LSHIFT: [0,-5,0], K_SPACE: [0,5,0]}
inputs_camera_rotate = {K_UP: [-.01,0,0], K_DOWN: [.01,0,0], K_LEFT: [0,-.01,0], K_RIGHT: [0,.01,0]} #, K_RCTRL: [0,0,.01], K_RSHIFT: [0,0,-.01]} #, K_u: [0,0,-1], K_o: [0,0,1]}
inputs_object_rotate = {K_i: Vector3(1,0,0), K_k: Vector3(-1,0,0), K_j: Vector3(0,1,0), K_l: Vector3(0,-1,0), K_u: Vector3(0,0,-1), K_o: Vector3(0,0,1)}

# Main loop
while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			quit()
		elif event.type == pygame.KEYDOWN:
			if event.key == K_ESCAPE:
				quit()
			if event.key in input_list:
				inputs[event.key] = True
			if event.key == K_t:
				render3D.selected_triangle += 1
				print(render3D.selected_triangle)
		elif event.type == pygame.KEYUP:
			if event.key in input_list:
				inputs[event.key] = False
		elif event.type == MOUSEWHEEL:
			Speed = min(max(1, Speed+Speed*event.y/10), 50)
	
	for i in input_list:
		if inputs[i]:
			if i in inputs_camera_move:
				render3D.camera.translate(Speed * np.array(inputs_camera_move[i]))
			if i in inputs_camera_rotate:
				render3D.camera.rotate(inputs_camera_rotate[i])
	
	mouse_move_x, mouse_move_y = pygame.mouse.get_rel()
	render3D.camera.rotate(np.array([mouse_move_y, mouse_move_x, 0])/360)
	pygame.mouse.set_pos(width/2, height/2)

	# Accessing the object information
	obj_list = render3D.objects_list

	# Rotating the light
	#for i in obj_list:
	#	if isinstance(i, render3D.lights.LightLike):
	#		i.direction = render3D.rotate_y(i.direction, 0.01)
	#cube = obj_list[0]
	#cube.offsets_center = render3D.rotate_points(cube.offsets_center - cube.position, -.008, .006, .005) + cube.position

	# Clearing the screen
	screen.fill((0,0,0))

	# Render all objects
	render3D.render(screen)

	pygame.mouse.get_rel()
	pygame.display.flip()
	clock.tick(75)