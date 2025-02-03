from PIL import Image
import sys, os

# Add parent directory to the path so that assignment modules can be imported.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import assignment1.vec
import assignment1.color
import assignment1.sphere
import assignment2.light

WIDTH = 300
HEIGHT = 300

viewport_size = 1.0
projection_plane_z = 1.0
camera_position = assignment1.vec.Vec(3, 0, 1)

# The camera rotation matrix (3x3) to transform viewport directions.
# [ [0.7071, 0, -0.7071],
#   [     0, 1,       0],
#   [0.7071, 0,  0.7071] ]
camera_rotation = [
    [0.7071, 0, -0.7071],
    [0,      1,  0],
    [0.7071, 0,  0.7071]
]

background_color = assignment1.color.Color(0, 0, 0)

# A very small number to avoid self-intersections.
EPSILON = 0.001

# Maximum recursion depth for reflections.
RECURSION_DEPTH = 3

# List of spheres in the scene.
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

# Global list for triangles (we will add the bunny triangles here)
triangles = []

# Define the lights in the scene.
lights = [
    assignment2.light.AmbientLight(intensity=0.2),
    assignment2.light.PointLight(intensity=0.6, position=assignment1.vec.Vec(2, 1, 0)),
    assignment2.light.DirectionalLight(intensity=0.2, direction=assignment1.vec.Vec(1, 4, 4))
]

# -------------------------------------------------------------
# Utility functions
# -------------------------------------------------------------

def canvas_to_viewport(x, y):
    """
    Converts 2D canvas coordinates (with origin at the center) into 3D viewport coordinates.
    """
    return assignment1.vec.Vec(
        x * viewport_size / WIDTH,
        y * viewport_size / HEIGHT,
        projection_plane_z
    )

def multiply_mv(mat, vec):
    """
    Multiplies a 3x3 matrix (list of lists) by a Vec.
    Returns a new Vec.
    """
    x, y, z = vec.x, vec.y, vec.z
    rx = mat[0][0] * x + mat[0][1] * y + mat[0][2] * z
    ry = mat[1][0] * x + mat[1][1] * y + mat[1][2] * z
    rz = mat[2][0] * x + mat[2][1] * y + mat[2][2] * z
    return assignment1.vec.Vec(rx, ry, rz)

# -------------------------------------------------------------
# Intersection routines for spheres and triangles
# -------------------------------------------------------------

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

def intersect_ray_triangle(origin, direction, triangle):
    """
    Implements the Möller–Trumbore algorithm.
    Returns t (distance along the ray) if there is an intersection,
    or float('inf') if there is no intersection.
    """
    epsilon = 1e-6
    edge1 = triangle.v1.sub(triangle.v0)
    edge2 = triangle.v2.sub(triangle.v0)
    h = direction.cross(edge2)
    a = edge1.dot(h)
    if abs(a) < epsilon:
        return float('inf')  # Ray is parallel to the triangle.
    f = 1 / a
    s = origin.sub(triangle.v0)
    u = f * s.dot(h)
    if u < 0 or u > 1:
        return float('inf')
    q = s.cross(edge1)
    v = f * direction.dot(q)
    if v < 0 or u + v > 1:
        return float('inf')
    t = f * edge2.dot(q)
    if t > EPSILON:
        return t
    else:
        return float('inf')

# -------------------------------------------------------------
# Triangle class
# -------------------------------------------------------------

class Triangle:
    def __init__(self, v0, v1, v2, color, specular, reflective):
        """
        v0, v1, v2: vertices (Vec objects)
        color: a Color object
        specular: specular exponent (int)
        reflective: reflection coefficient (float between 0 and 1)
        """
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2
        self.color = color
        self.specular = specular
        self.reflective = reflective
        self.edge1 = self.v1.sub(self.v0)
        self.edge2 = self.v2.sub(self.v0)
        self.normal = self.edge1.cross(self.edge2).normalize()

# -------------------------------------------------------------
# OBJ file loader for the bunny model
# -------------------------------------------------------------

def load_obj(filename, color, specular, reflective):
    """
    Loads a Wavefront OBJ file.
    Returns a list of Triangle objects with the given color, specular and reflective values.
    Note: This basic loader assumes that faces are triangles.
    """
    vertices = []
    tris = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('v '):
                parts = line.split()
                x = float(parts[1])
                y = float(parts[2])
                z = float(parts[3])
                vertices.append(assignment1.vec.Vec(x, y, z))
            elif line.startswith('f '):
                parts = line.split()
                # OBJ indices are 1-indexed; also ignore any texture/normal info.
                idx0 = int(parts[1].split('/')[0]) - 1
                idx1 = int(parts[2].split('/')[0]) - 1
                idx2 = int(parts[3].split('/')[0]) - 1
                v0 = vertices[idx0]
                v1 = vertices[idx1]
                v2 = vertices[idx2]
                tris.append(Triangle(v0, v1, v2, color, specular, reflective))
    return tris

# -------------------------------------------------------------
# Intersection and shading routines that consider all objects
# -------------------------------------------------------------

def closest_intersection(origin, direction, t_min, t_max):
    """
    Finds the closest object (sphere or triangle) intersected by the ray (if any)
    within the range (t_min, t_max).
    Returns a tuple (object, t) or None if there is no intersection.
    """
    closest_t = float('inf')
    closest_obj = None

    # Check intersections with spheres.
    for sphere in spheres:
        t1, t2 = intersect_ray_sphere(origin, direction, sphere)
        if t_min < t1 < t_max and t1 < closest_t:
            closest_t = t1
            closest_obj = sphere
        if t_min < t2 < t_max and t2 < closest_t:
            closest_t = t2
            closest_obj = sphere

    # Check intersections with triangles.
    for triangle in triangles:
        t = intersect_ray_triangle(origin, direction, triangle)
        if t_min < t < t_max and t < closest_t:
            closest_t = t
            closest_obj = triangle

    if closest_obj is None:
        return None
    return (closest_obj, closest_t)

def compute_lighting(point, normal, view, specular):
    """
    Computes the lighting at a point on a surface.
    Takes into account diffuse and specular contributions as well as shadows.
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

            # Shadow check: if an object blocks the light, skip its contribution.
            if closest_intersection(point, L, EPSILON, t_max) is not None:
                continue

            # Diffuse reflection.
            n_dot_l = normal.dot(L)
            if n_dot_l > 0:
                intensity += light.intensity * n_dot_l / (normal.length() * L.length())

            # Specular reflection.
            if specular != -1:
                R = normal.mul(2 * n_dot_l).sub(L)  # Reflection vector.
                r_dot_v = R.dot(view)
                if r_dot_v > 0:
                    intensity += light.intensity * (r_dot_v / (R.length() * view.length())) ** specular

    return intensity

def reflect_ray(incident, normal):
    """
    Computes the reflection of the incident ray with respect to the normal.
    Reflection formula: R = 2*(incident · normal)*normal - incident.
    """
    return normal.mul(2 * incident.dot(normal)).sub(incident)

def trace_ray(origin, direction, t_min, t_max, depth):
    """
    Traces a ray into the scene. If the ray hits an object, computes the local color
    using diffuse and specular lighting and recursively computes reflections.
    """
    intersection = closest_intersection(origin, direction, t_min, t_max)
    if intersection is None:
        return background_color

    closest_obj, closest_t = intersection
    point = origin.add(direction.mul(closest_t))
    if isinstance(closest_obj, assignment1.sphere.Sphere):
        # For a sphere, the normal is computed from the center.
        normal = point.sub(closest_obj.center).div(point.sub(closest_obj.center).length())
    elif isinstance(closest_obj, Triangle):
        # For a triangle, we use the precomputed face normal.
        normal = closest_obj.normal
    else:
        normal = assignment1.vec.Vec(0, 0, 0)  # Should not occur.

    view = direction.mul(-1)
    lighting = compute_lighting(point, normal, view, closest_obj.specular)
    local_color = closest_obj.color.mul(lighting)

    # If the object is not reflective or we've reached the recursion limit, return the local color.
    if closest_obj.reflective <= 0 or depth <= 0:
        return local_color

    reflected_ray = reflect_ray(view, normal)
    reflected_color = trace_ray(point, reflected_ray, EPSILON, float('inf'), depth - 1)
    return local_color.mul(1 - closest_obj.reflective).add(reflected_color.mul(closest_obj.reflective))

# -------------------------------------------------------------
# Main render function
# -------------------------------------------------------------

def render_scene():
    """
    Renders the scene pixel-by-pixel and returns a PIL Image.
    """
    img = Image.new("RGB", (WIDTH, HEIGHT))
    pixels = img.load()

    for px in range(-WIDTH // 2, WIDTH // 2):
        for py in range(-HEIGHT // 2, HEIGHT // 2):
            direction = canvas_to_viewport(px, py)
            # Apply the camera rotation.
            direction = multiply_mv(camera_rotation, direction)
            color = trace_ray(camera_position, direction, 1.0, float('inf'), RECURSION_DEPTH)

            fx = px + WIDTH // 2
            fy = HEIGHT // 2 - py - 1

            r = max(min(int(color.r), 255), 0)
            g = max(min(int(color.g), 255), 0)
            b = max(min(int(color.b), 255), 0)
            pixels[fx, fy] = (r, g, b)

    return img

# -------------------------------------------------------------
# Main: load the bunny model and render the scene.
# -------------------------------------------------------------

if __name__ == "__main__":
    # Load the Stanford Bunny from an OBJ file.
    # Ensure that "bunny.obj" is in the same directory as this script.
    try:
        bunny_triangles = load_obj("bunny.obj",
                                   color=assignment1.color.Color(200, 200, 200),
                                   specular=10,
                                   reflective=0.2)
        # Optionally scale and translate the bunny so it appears in the scene.
        bunny_scale = 1.0
        bunny_translation = assignment1.vec.Vec(1, -1.5, 4)
        for tri in bunny_triangles:
            tri.v0 = tri.v0.mul(bunny_scale).add(bunny_translation)
            tri.v1 = tri.v1.mul(bunny_scale).add(bunny_translation)
            tri.v2 = tri.v2.mul(bunny_scale).add(bunny_translation)
            # Recompute edges and normal after transformation.
            tri.edge1 = tri.v1.sub(tri.v0)
            tri.edge2 = tri.v2.sub(tri.v0)
            tri.normal = tri.edge1.cross(tri.edge2).normalize()
        triangles.extend(bunny_triangles)
    except Exception as e:
        print("Error loading bunny.obj:", e)

    image = render_scene()
    image.save("assignment_4_output.png")
