from PIL import Image
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import assignment1.vec
import assignment1.color
import assignment1.sphere
import assignment2.light


WIDTH = 500
HEIGHT = 500

# Viewport and camera settings.
viewport_size = 1.0
projection_plane_z = 1.0
camera_position = assignment1.vec.Vec(0, 0, 0)

background_color = assignment1.color.Color(0, 0, 0)

# A very small number to avoid self-intersections.
EPSILON = 0.001

# Maximum recursion depth for reflections.
RECURSION_DEPTH = 3

spheres = [
    assignment1.sphere.Sphere(assignment1.vec.Vec(0, -1, 3), 1,
                                assignment1.color.Color(255, 0, 0), 500, 0.2),  
    assignment1.sphere.Sphere(assignment1.vec.Vec(-2, 0, 4), 1,
                                assignment1.color.Color(0, 255, 0), 10, 0.4),   
    assignment1.sphere.Sphere(assignment1.vec.Vec(2, 0, 4), 1,
                                assignment1.color.Color(0, 0, 255), 500, 0.3),  
    assignment1.sphere.Sphere(assignment1.vec.Vec(0, -5001, 0), 5000,
                                assignment1.color.Color(255, 255, 0), 1000, 0.5)
]

lights = [
    assignment2.light.AmbientLight(intensity=0.2),
    assignment2.light.PointLight(intensity=0.6, position=assignment1.vec.Vec(2, 1, 0)),
    assignment2.light.DirectionalLight(intensity=0.2, direction=assignment1.vec.Vec(1, 4, 4))
]


def canvas_to_viewport(x, y):
    """
    Converts 2D canvas coordinates (with origin at center) into 3D viewport coordinates.
    """
    return assignment1.vec.Vec(
        x * viewport_size / WIDTH,
        y * viewport_size / HEIGHT,
        projection_plane_z
    )

def intersect_ray_sphere(origin, direction, sphere):
    """
    Computes the intersections (t values) of a ray with a sphere.
    Returns a tuple (t1, t2); if there is no intersection, returns (inf, inf).
    """
    oc = origin.sub(sphere.center)
    k1 = direction.dot(direction)
    k2 = 2 * oc.dot(direction)
    k3 = oc.dot(oc) - sphere.radius**2

    discriminant = k2 * k2 - 4 * k1 * k3
    if discriminant < 0:
        return float('inf'), float('inf')
    from math import sqrt
    sqrt_d = sqrt(discriminant)
    t1 = (-k2 + sqrt_d) / (2 * k1)
    t2 = (-k2 - sqrt_d) / (2 * k1)
    return t1, t2

def closest_intersection(origin, direction, t_min, t_max):
    """
    Finds the closest sphere intersected by the ray (if any) within (t_min, t_max).
    Returns a tuple (sphere, t) if an intersection is found, or None otherwise.
    This function is used both for finding the primary intersection and for shadow checking.
    """
    closest_t = float('inf')
    closest_sphere = None

    for sphere in spheres:
        t1, t2 = intersect_ray_sphere(origin, direction, sphere)
        if t_min < t1 < t_max and t1 < closest_t:
            closest_t = t1
            closest_sphere = sphere
        if t_min < t2 < t_max and t2 < closest_t:
            closest_t = t2
            closest_sphere = sphere

    if closest_sphere is None:
        return None
    return (closest_sphere, closest_t)

def compute_lighting(point, normal, view, specular):
    """
    Computes the lighting at a given point on a surface with the given normal.
    The 'specular' parameter is the specular exponent (if -1, then the surface is not shiny).
    This function takes shadows into account by casting a shadow ray toward each light.
    """
    intensity = 0.0

    for light in lights:
        if isinstance(light, assignment2.light.AmbientLight):
            intensity += light.intensity
        else:
            if isinstance(light, assignment2.light.PointLight):
                L = light.position.sub(point)
                t_max = 1.0
            elif isinstance(light, assignment2.light.DirectionalLight):
                L = light.direction
                t_max = float('inf')
            else:
                continue

            # Shadow check: if there is any object between the point and the light,
            # skip this light's contribution.
            if closest_intersection(point, L, EPSILON, t_max) is not None:
                continue

            # Diffuse reflection.
            n_dot_l = normal.dot(L)
            if n_dot_l > 0:
                intensity += light.intensity * n_dot_l / (normal.length() * L.length())

            # Specular reflection.
            if specular != -1:
                # Reflect L around normal: R = 2*(N dot L)*N - L.
                R = normal.mul(2 * n_dot_l).sub(L)
                r_dot_v = R.dot(view)
                if r_dot_v > 0:
                    intensity += light.intensity * (r_dot_v / (R.length() * view.length())) ** specular

    return intensity

def reflect_ray(incident, normal):
    """
    Computes the reflection of the incident ray around the normal.
    (Incident and normal are assumed to be Vec objects.)
    """
    # Reflection formula: R = 2*(incident dot normal)*normal - incident.
    return normal.mul(2 * incident.dot(normal)).sub(incident)

def trace_ray(origin, direction, t_min, t_max, depth):
    """
    Traces a ray into the scene. If the ray hits an object, computes the local color
    (using diffuse and specular lighting) and, if the object is reflective and depth > 0,
    recursively computes the reflected color.
    Returns a Color.
    """
    intersection = closest_intersection(origin, direction, t_min, t_max)
    if intersection is None:
        return background_color

    closest_sphere, closest_t = intersection

    # Compute the intersection point and the surface normal.
    point = origin.add(direction.mul(closest_t))
    normal = point.sub(closest_sphere.center).div(point.sub(closest_sphere.center).length())
    view = direction.mul(-1)

    # Compute lighting (diffuse and specular).
    lighting = compute_lighting(point, normal, view, closest_sphere.specular)
    local_color = closest_sphere.color.mul(lighting)

    # If the object is non-reflective or we've reached the recursion limit, return the local color.
    if closest_sphere.reflective <= 0 or depth <= 0:
        return local_color

    # Otherwise, compute the color due to the reflection.
    reflected_ray = reflect_ray(view, normal)
    reflected_color = trace_ray(point, reflected_ray, EPSILON, float('inf'), depth - 1)

    # Combine the local color with the reflected color.
    return local_color.mul(1 - closest_sphere.reflective).add(reflected_color.mul(closest_sphere.reflective))

def render_scene():
    """
    Renders the scene pixel-by-pixel and returns a PIL Image.
    """
    img = Image.new("RGB", (WIDTH, HEIGHT))
    pixels = img.load()

    for px in range(-WIDTH // 2, WIDTH // 2):
        for py in range(-HEIGHT // 2, HEIGHT // 2):
            direction = canvas_to_viewport(px, py)
            color = trace_ray(camera_position, direction, 1.0, float('inf'), RECURSION_DEPTH)

            fx = px + WIDTH // 2
            fy = HEIGHT // 2 - py - 1

            # Clamp color components to the range [0, 255].
            r = max(min(int(color.r), 255), 0)
            g = max(min(int(color.g), 255), 0)
            b = max(min(int(color.b), 255), 0)
            pixels[fx, fy] = (r, g, b)

    return img


if __name__ == "__main__":
    image = render_scene()
    image.save("assignment_3_output.png")
