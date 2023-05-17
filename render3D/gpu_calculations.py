from numpy import array
from numba import jit, cuda # For GPU processing

@jit(target_backend='cuda')
def dot_product(a, b):
	return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]

@jit(target_backend='cuda')
def cross_product(a, b):
	return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]

@jit(target_backend='cuda')
def normalize(vector):
	return vector/(vector[0]**2+vector[1]**2+vector[2]**2)**.5

@jit(target_backend='cuda')
def calc_normal(triangle):
	line1, line2 = triangle[0:2] - triangle[2]
	normal = array(cross_product(line1, line2))
	#normal = normalize(normal) in case of some kind of crash try uncommenting this line
	return normal

@jit(target_backend='cuda')
def calc_triangle_center(ts):
	"""ts = triangles"""	
	return [(ts[0][0]+ts[1][0]+ts[2][0])/3, (ts[0][1]+ts[1][1]+ts[2][1])/3, (ts[0][2]+ts[1][2]+ts[2][2])/3]