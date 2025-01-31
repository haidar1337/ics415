from light import *
from PIL import Image

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import assignment1.vec
import assignment1.color
import assignment1.sphere

WIDTH = 500
HEIGHT = 500

# Viewport and camera
viewport_size = 1.0
projection_plane_z = 1.0
camera_position = assignment1.vec.Vec(0, 0, 0)

# Background color (white)
background_color = assignment1.color.Color(255, 255, 255)

# Spheres (just like in the JS code)
spheres = [
    assignment1.sphere.Sphere(assignment1.vec.Vec(0, -1, 3), 1, assignment1.color.Color(255, 0, 0), 500),   # red sphere
    assignment1.sphere.Sphere(assignment1.vec.Vec(-2, 0, 4), 1, assignment1.color.Color(0, 255, 0), 10),    # green sphere
    assignment1.sphere.Sphere(assignment1.vec.Vec(2, 0, 4), 1, assignment1.color.Color(0, 0, 255), 500),    # blue sphere
    assignment1.sphere.Sphere(assignment1.vec.Vec(0, -5001, 0), 5000, assignment1.color.Color(255, 255, 0), 1000)  # yellow floor
]

# Lights
lights = [
    AmbientLight(intensity=0.2),
    PointLight(intensity=0.6, position=assignment1.vec.Vec(2, 1, 0)),
    DirectionalLight(intensity=0.2, direction=assignment1.vec.Vec(1, 4, 4))
]

# --------------------------------------------------------------
# Helper functions
# --------------------------------------------------------------

def canvas_to_viewport(x, y):
    """
    Converts 2D canvas coordinates (x, y) into 3D viewport coordinates.
    """
    return assignment1.vec.Vec(
        x * viewport_size / WIDTH,
        y * viewport_size / HEIGHT,
        projection_plane_z
    )

def intersect_ray_sphere(origin, direction, sphere):
    """
    Returns the two solutions (t1, t2) for the intersection of a
    ray (origin + t*direction) with a sphere.
    """
    # oc = origin - center
    oc = origin.sub(sphere.center)

    k1 = direction.dot(direction)  # direction^2
    k2 = 2 * oc.dot(direction)
    k3 = oc.dot(oc) - sphere.radius**2

    discriminant = k2*k2 - 4*k1*k3
    if discriminant < 0:
        return float('inf'), float('inf')  # No intersection

    from math import sqrt
    sqrt_d = sqrt(discriminant)
    t1 = (-k2 + sqrt_d) / (2 * k1)
    t2 = (-k2 - sqrt_d) / (2 * k1)
    return t1, t2

def compute_lighting(point, normal, view, specular):
    """
    Computes the lighting at a given point with the given normal and view vectors.
    specular: the specular exponent for the object (if -1, means no specular).
    """
    intensity = 0.0
    n_len = normal.length()
    v_len = view.length()

    for light in lights:
        if isinstance(light, AmbientLight):
            # Ambient light
            intensity += light.intensity
        else:
            # Point or Directional
            if isinstance(light, PointLight):
                # L = light.position - point
                L = light.position.sub(point)
            else:  # DirectionalLight
                # L = light.direction (already a direction)
                L = light.direction

            # Diffuse component
            n_dot_l = normal.dot(L)
            if n_dot_l > 0:
                intensity += light.intensity * n_dot_l / (n_len * L.length())

            # Specular component
            if specular != -1:
                # R = 2*(N dot L)*N - L
                R = normal.mul(2 * n_dot_l).sub(L)
                r_dot_v = R.dot(view)
                if r_dot_v > 0:
                    intensity += light.intensity * (r_dot_v / (R.length() * v_len))**specular

    return intensity

def trace_ray(origin, direction, t_min, t_max):
    """
    Traces the ray and returns the Color of the closest intersected sphere,
    or the background color if none is found.
    """
    closest_t = float('inf')
    closest_sphere = None

    # Find the closest intersection
    for sphere in spheres:
        t1, t2 = intersect_ray_sphere(origin, direction, sphere)

        # Check t1
        if t_min < t1 < t_max and t1 < closest_t:
            closest_t = t1
            closest_sphere = sphere

        # Check t2
        if t_min < t2 < t_max and t2 < closest_t:
            closest_t = t2
            closest_sphere = sphere

    if closest_sphere is None:
        return background_color

    # Compute intersection point and normal
    point = origin.add(direction.mul(closest_t))
    normal = point.sub(closest_sphere.center)
    normal = normal.div(normal.length())  # normalize

    view = direction.mul(-1)
    lighting = compute_lighting(point, normal, view, closest_sphere.specular)

    shaded_color = closest_sphere.color.mul(lighting)
    return shaded_color


def render_scene():
    img = Image.new("RGB", (WIDTH, HEIGHT))
    pixels = img.load()

    for px in range(-WIDTH//2, WIDTH//2):
        for py in range(-HEIGHT//2, HEIGHT//2):
            # Convert canvas coords to viewport coords
            direction = canvas_to_viewport(px, py)
            color = trace_ray(camera_position, direction, 1.0, float('inf'))

            # Translate (px, py) from center-based coords to image coords
            fx = px + WIDTH//2
            fy = HEIGHT//2 - py - 1

            # Clamp color components to [0,255]
            r = max(min(int(color.r), 255), 0)
            g = max(min(int(color.g), 255), 0)
            b = max(min(int(color.b), 255), 0)

            pixels[fx, fy] = (r, g, b)

    return img

if __name__ == "__main__":
    image = render_scene()
    image.save("assignment_2_output.png")