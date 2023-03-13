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
object_list.append(render3D.shapes.cuboid([0,0,1000], [500, 500, 500], None))



# Key input handler
input_list = [K_w, K_s, K_a, K_d, K_q, K_e, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_RCTRL, K_RSHIFT, K_i, K_k, K_j, K_l, K_u, K_o]
inputs = {}
for i in input_list:
	inputs[i] = False
inputs_camera_move = {K_w: [0,0,5], K_s: [0,0,-5], K_a: [-5,0,0], K_d: [5,0,0], K_q: [0,5,0], K_e: [0,-5,0]}
inputs_camera_rotate = {K_UP: [.01,0,0], K_DOWN: [-.01,0,0], K_LEFT: [0,-.01,0], K_RIGHT: [0,.01,0], K_RCTRL: [0,0,.01], K_RSHIFT: [0,0,-.01]} #, K_u: [0,0,-1], K_o: [0,0,1]}
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
			#if i in inputs_object_rotate:
			#	ObjectOffsets = RotateObject(ObjectOffsets, inputs_camera_move[i])



	# Render all objects
	projections = render3D.render(object_list)

	# Clearing the screen
	screen.fill((0,0,0))

	# Drawing object on screen
	for i in projections:
		pygame.draw.lines(screen, (255,255,255), True, i[:4], width=2)
		pygame.draw.lines(screen, (255,255,255), True, i[4:8], width=2)
		for j in range(4):
			pygame.draw.line(screen, (255,255,255), i[j], i[4+j], width=2)

	pygame.display.flip()
	clock.tick(75)