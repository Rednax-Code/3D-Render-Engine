import pygame
import pygame.gfxdraw
from pygame.locals import *
from pygame.math import *
import render3D

# Initializing window
pygame.init()
width, height = 1920, 1080
flags = pygame.HWSURFACE | pygame.DOUBLEBUF
screen = pygame.display.set_mode((width, height), flags, vsync=1)
pygame.display.set_caption("3D")
clock = pygame.time.Clock()


# Initializing renderer
render3D.init()


# Creating list for objects
object_list = []

# Adding first shape
object_list.append(render3D.shapes.cuboid([0,0,1000], [2, 2, 2], None))



# Key input handler
input_list = [K_z, K_x, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_i, K_k, K_j, K_l, K_u, K_o]
inputs = {}
for i in input_list:
	inputs[i] = False
inputs_camera_move = {K_z: Vector3(0,0,0.02), K_x: Vector3(0,0,-0.02), K_UP: Vector3(0,0.02,0), K_DOWN: Vector3(0,-0.02,0), K_LEFT: Vector3(0.02,0,0), K_RIGHT: Vector3(-0.02,0,0)}
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
	
	#for i in input_list:
	#	if inputs[i]:
	#		if i in inputs_camera_move:
	#			Camera['Pos'] += inputs_camera_move[i]
	#		if i in inputs_object_rotate:
	#			ObjectOffsets = RotateObject(ObjectOffsets, inputs_camera_move[i])



	# Render all objects
	render3D.render(object_list)

	# Clearing the screen
	screen.fill((0,0,0))

	# Drawing object on screen
	pass

	pygame.display.flip()
	clock.tick(75)