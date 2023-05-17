"""
Render3D
--------

A 3D renderer originally created for pygame.

I started on this project around the start of march 2023.
What i plan to do with it all... idk, BUT it's great fun.
It is currently VERY slow (cus it's python), but i'll probably add some Cython magic.

Update:
It's currently the 17th of may 2023.
It renders a heck of a lot faster now because i transfered some load to the gpu.

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

from render3D.base import *
from render3D.lights import *
from render3D.shapes import *

__version__ = ':)'

print('render3D', __version__)

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

	global objects_list
	objects_list = []

	global selected_triangle # Temp
	selected_triangle = 0

	init_base(screen_size, camera, objects_list, selected_triangle)

def test():
	try:
		import render3D.base
		import render3D.lights
		import render3D.shapes
		print('works')
		del render3D.base, render3D.lights, render3D.shapes
	except:
		print('oh no...')

# Base64
# VGhpcyBjb2RlIHdhcyB3cml0dGVuIGJ5IFJlZG5heEdhbWluZyBvbiBnaXRodWI=