"""
Shapes
------

Defines the shapes for render3D.py
"""
import numpy as np
import numpy.typing as npt


class LightLike:
	pass

class ambient_light(LightLike):
	def __init__(self, intensity:float, color:list):
		"""
		Just... light

		Parameters
		----------
		intensity : float
			How strong the light is.
		
		color : list[r, g, b]
			The color

		Returns
		-------
		LightLike
		"""

		self.intensity = intensity
		self.color = color

class directional_light(LightLike):
	def __init__(self, direction:npt.ArrayLike, intensity:float, color:list):
		"""
		Light with a single direction

		Parameters
		----------
		direction : Array[x: float, y: float, z: float]
			The direction of the light
			
		intensity : float
			How strong the light is.
		
		color : list[r, g, b]
			The color

		Returns
		-------
		LightLike
		"""

		self.direction = np.array(direction)
		self.intensity = intensity
		self.color = color

class point_light(LightLike):
	def __init__(self, position:npt.ArrayLike, intensity:float, color:list):
		"""
		Light going in all directions equally spread

		Parameters
		----------
		position : Array[x: float, y: float, z: float]
			The position of the light
			
		intensity : float
			How strong the light is.
		
		color : list[r, g, b]
			The color

		Returns
		-------
		LightLike
		"""

		self.position = np.array(position)
		self.intensity = intensity
		self.color = color