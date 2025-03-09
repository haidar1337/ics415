from PIL import Image
from sphere import Sphere
from vec import Vec
from color import Color

canvas_width = 500
canvas_height = 500

image = Image.new("RGB", (canvas_width, canvas_height), (255, 255, 255))
pixels = image.load()


def put_pixel(x, y, color):
    x = canvas_width // 2 + x
    y = canvas_height // 2 - y - 1
    
    if 0 <= x < canvas_width and 0 <= y < canvas_height:
        pixels[x, y] = (color.r, color.g, color.b)




viewport_size = 1
projection_plane_z = 1
camera_position = Vec(0, 0, 0)
background_color = Color(255, 255, 255)

spheres = [
    Sphere(Vec(0, -1, 3), 1, Color(255, 0, 0)),
    Sphere(Vec(-2, 0, 4), 1, Color(0, 255, 0)),
    Sphere(Vec(2, 0, 4), 1, Color(0, 0, 255)),
]

def canvas_to_viewport(x, y):
    return Vec(
        x * viewport_size / canvas_width,
        y * viewport_size / canvas_height,
        projection_plane_z
    )

def intersect_ray_sphere(origin, direction, sphere):
    oc = origin.sub(sphere.center)
    
    k1 = direction.dot(direction)
    k2 = 2 * oc.dot(direction)
    k3 = oc.dot(oc) - sphere.radius ** 2
    
    discriminant = k2 ** 2 - 4 * k1 * k3
    if discriminant < 0:
        return float('inf'), float('inf')

    from math import sqrt 
    t1 = (-k2 + sqrt(discriminant)) / (2 * k1)
    t2 = (-k2 - sqrt(discriminant)) / (2 * k1)
    return t1, t2

def trace_ray(origin, direction, min_t, max_t):
    closest_t = float('inf')
    closest_sphere = None
    
    for sphere in spheres:
        t1, t2 = intersect_ray_sphere(origin, direction, sphere)
        if min_t < t1 < max_t and t1 < closest_t:
            closest_t = t1
            closest_sphere = sphere
        if min_t < t2 < max_t and t2 < closest_t:
            closest_t = t2
            closest_sphere = sphere
    
    if closest_sphere is None:
        return background_color
    
    return closest_sphere.color

for x in range(-canvas_width // 2, canvas_width // 2):
    for y in range(-canvas_height // 2, canvas_height // 2):
        direction = canvas_to_viewport(x, y)
        color = trace_ray(camera_position, direction, 1, float('inf'))
        put_pixel(x, y, color)

image.save('assignment_1_output.png')
 