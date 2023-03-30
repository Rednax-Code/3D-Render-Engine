from scipy.spatial.transform import Rotation as R
import numpy as np
import numpy.typing as npt


def rotate_x(points:npt.ArrayLike, y:float):
	r = R.from_euler('x', y)
	return r.as_matrix().dot(points.T).T

def rotate_y(points:npt.ArrayLike, b:float):
	r = R.from_euler('y', b)
	return r.as_matrix().dot(points.T).T

def rotate_z(points:npt.ArrayLike, a:float):
	r = R.from_euler('z', a)
	return r.as_matrix().dot(points.T).T

def rotate_points(points:npt.ArrayLike, a:float, b:float, y:float):
	return rotate_x(rotate_y(rotate_z(points, y), b), a)