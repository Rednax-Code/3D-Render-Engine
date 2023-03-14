import pygame
import pygame.gfxdraw
from pygame.locals import *
from pygame.math import *
import render3D
import os.path


# Initializing window
pygame.init()
width, height = 1280, 720
flags = pygame.HWSURFACE | pygame.DOUBLEBUF
screen = pygame.display.set_mode((width, height), flags, vsync=1)
pygame.display.set_caption("3D")
clock = pygame.time.Clock()


# Initializing renderer
render3D.init([width, height])

# Loading in triangle meshes
shape = os.path.join(os.path.dirname(__file__),'objects\\test.obj')

# Adding first shapes
render3D.scene.add_objects([
	render3D.shapes.mesh(shape, [0,0,200], [500,500,500], None),
    #render3D.shapes.cuboid([0,0,2000], [500, 500, 500], None),
    render3D.lights.single_direction_light([0,0,-1], 1, [255,255,255])
])


# Key input handler
input_list = [K_w, K_s, K_a, K_d, K_q, K_e, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_RCTRL, K_RSHIFT, K_i, K_k, K_j, K_l, K_u, K_o]
inputs = {}
for i in input_list:
	inputs[i] = False
inputs_camera_move = {K_w: [0,0,5], K_s: [0,0,-5], K_a: [-5,0,0], K_d: [5,0,0], K_q: [0,-5,0], K_e: [0,5,0]}
inputs_camera_rotate = {K_UP: [-.01,0,0], K_DOWN: [.01,0,0], K_LEFT: [0,-.01,0], K_RIGHT: [0,.01,0]} #, K_RCTRL: [0,0,.01], K_RSHIFT: [0,0,-.01]} #, K_u: [0,0,-1], K_o: [0,0,1]}
inputs_object_rotate = {K_i: Vector3(1,0,0), K_k: Vector3(-1,0,0), K_j: Vector3(0,1,0), K_l: Vector3(0,-1,0), K_u: Vector3(0,0,-1), K_o: Vector3(0,0,1)}

# Main loop
while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			quit()
		if event.type == pygame.KEYDOWN:
			if event.key == K_ESCAPE:
				quit()
			if event.key in input_list:
				inputs[event.key] = True
		if event.type == pygame.KEYUP:
			if event.key in input_list:
				inputs[event.key] = False
	
	for i in input_list:
		if inputs[i]:
			if i in inputs_camera_move:
				render3D.camera.translate(inputs_camera_move[i])
			if i in inputs_camera_rotate:
				render3D.camera.rotate(inputs_camera_rotate[i])


	obj_list = render3D.objects_list

	# Rotating the light
	#for i in obj_list:
	#	if isinstance(i, render3D.lights.LightLike):
	#		i.direction = render3D.rotate_y(i.direction, 0.01)
	#cube.offsets_center = render3D.rotate_points(cube.offsets_center - cube.position, .005, .003, .004) + cube.position

	# Clearing the screen
	screen.fill((0,0,0))

	# Render all objects
	render3D.render(screen)

	pygame.display.flip()
	clock.tick(75)