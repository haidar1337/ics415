from PIL import Image
from math import sqrt
import sys, os

# ------------------------------------------------------------
# Basic Classes: Vec, Color, Sphere, Light, Triangle, Cylinder
# ------------------------------------------------------------

class Vec:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def dot(self, vec):
        return self.x * vec.x + self.y * vec.y + self.z * vec.z

    def sub(self, vec):
        return Vec(self.x - vec.x, self.y - vec.y, self.z - vec.z)

    def add(self, vec):
        return Vec(self.x + vec.x, self.y + vec.y, self.z + vec.z)

    def mul(self, num):
        return Vec(self.x * num, self.y * num, self.z * num)

    def div(self, num):
        return Vec(self.x / num, self.y / num, self.z / num)

    def length(self):
        return sqrt(self.x**2 + self.y**2 + self.z**2)

    def cross(self, vec):
        return Vec(self.y * vec.z - self.z * vec.y,
                   self.z * vec.x - self.x * vec.z,
                   self.x * vec.y - self.y * vec.x)

    def normalize(self):
        l = self.length()
        if l == 0:
            raise ValueError("Cannot normalize a zero-length vector")
        return self.div(l)

class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def mul(self, num):
        return Color(self.r * num, self.g * num, self.b * num)

    def add(self, other):
        return Color(self.r + other.r, self.g + other.g, self.b + other.b)

class Sphere:
    def __init__(self, center, radius, color, specular=0, reflective=0):
        self.center = center
        self.radius = radius
        self.color = color
        self.specular = specular
        self.reflective = reflective
        self.transparency = 0  # Opaque

class Light:
    def __init__(self, intensity):
        self.intensity = intensity

class AmbientLight(Light):
    def __init__(self, intensity):
        super().__init__(intensity)

class PointLight(Light):
    def __init__(self, intensity, position):
        super().__init__(intensity)
        self.position = position

class DirectionalLight(Light):
    def __init__(self, intensity, direction):
        super().__init__(intensity)
        self.direction = direction

class Triangle:
    def __init__(self, v0, v1, v2, color, specular, reflective):
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2
        self.color = color
        self.specular = specular
        self.reflective = reflective
        self.transparency = 0  # Opaque
        self.edge1 = self.v1.sub(self.v0)
        self.edge2 = self.v2.sub(self.v0)
        self.normal = self.edge1.cross(self.edge2).normalize()

class Cylinder:
    def __init__(self, base, axis, height, radius, color, specular, reflective, transparency=0):
        """
        base: Vec for the bottom-center of the cylinder.
        axis: Vec (will be normalized).
        height: finite height.
        radius: cylinder radius.
        color, specular, reflective: material properties.
        transparency: values from 0 (opaque) to 1 (fully transparent).
        """
        self.base = base
        self.axis = axis.normalize()
        self.height = height
        self.radius = radius
        self.color = color
        self.specular = specular
        self.reflective = reflective
        self.transparency = transparency

# ------------------------------------------------------------
# Global Settings and Scene Object Lists
# ------------------------------------------------------------

# Use a 300×300 resolution.
WIDTH = 300
HEIGHT = 300
viewport_size = 1.0
projection_plane_z = 1.0

# Camera at the origin, looking along +z.
camera_position = Vec(0, 0, 0)

background_color = Color(0, 0, 0)
EPSILON = 0.001
RECURSION_DEPTH = 3

# Scene objects:
# --- Sphere: shiny red reflective sphere.
spheres = [
    Sphere(center=Vec(0.5, 0, 4), radius=1, color=Color(255, 0, 0), specular=500, reflective=0.8)
]

# --- Cylinder: dark blue, refractive (transparent) cylinder.
cylinders = [
    Cylinder(
        base=Vec(-0.5, -1, 3),
        axis=Vec(0, 1, 0),
        height=2,
        radius=0.8,
        color=Color(0, 0, 139),
        specular=50,
        reflective=0,
        transparency=0.7
    )
]

# --- Bunny: loaded from OBJ (will be white).
triangles = []  # to be filled by the OBJ loader

# Lights.
lights = [
    AmbientLight(0.2),
    PointLight(0.6, Vec(2, 1, 0)),
    DirectionalLight(0.2, Vec(1, 4, 4))
]

# Global bounding box for the bunny (for optimization).
bunny_bbox_min = None
bunny_bbox_max = None

# ------------------------------------------------------------
# Utility Functions
# ------------------------------------------------------------

def canvas_to_viewport(x, y):
    """Map 2D canvas coordinates (origin at center) to 3D viewport coordinates."""
    return Vec(
        x * viewport_size / WIDTH,
        y * viewport_size / HEIGHT,
        projection_plane_z
    )

def ray_intersect_aabb(origin, direction, box_min, box_max):
    """Simple ray-AABB intersection test."""
    tmin = (box_min.x - origin.x) / direction.x if direction.x != 0 else -float('inf')
    tmax = (box_max.x - origin.x) / direction.x if direction.x != 0 else float('inf')
    if tmin > tmax: tmin, tmax = tmax, tmin

    tymin = (box_min.y - origin.y) / direction.y if direction.y != 0 else -float('inf')
    tymax = (box_max.y - origin.y) / direction.y if direction.y != 0 else float('inf')
    if tymin > tymax: tymin, tymax = tymax, tymin

    if (tmin > tymax) or (tymin > tmax):
        return False

    tmin = max(tmin, tymin)
    tmax = min(tmax, tymax)

    tzmin = (box_min.z - origin.z) / direction.z if direction.z != 0 else -float('inf')
    tzmax = (box_max.z - origin.z) / direction.z if direction.z != 0 else float('inf')
    if tzmin > tzmax: tzmin, tzmax = tzmax, tzmin

    if (tmin > tzmax) or (tzmin > tmax):
        return False

    return tmax >= max(tmin, 0)

def refract_ray(incident, normal, n1, n2):
    """
    Computes the refracted ray direction using Snell's law.
    Both incident and normal should be normalized.
    Returns a normalized Vec or None in case of total internal reflection.
    """
    eta = n1 / n2
    cos_i = -normal.dot(incident)
    sin_t2 = eta * eta * (1 - cos_i * cos_i)
    if sin_t2 > 1:
        return None  # Total internal reflection.
    cos_t = sqrt(1 - sin_t2)
    refracted = incident.mul(eta).add(normal.mul(eta * cos_i - cos_t))
    return refracted.normalize()

# ------------------------------------------------------------
# Intersection Routines
# ------------------------------------------------------------

def intersect_ray_sphere(origin, direction, sphere):
    oc = origin.sub(sphere.center)
    k1 = direction.dot(direction)
    k2 = 2 * oc.dot(direction)
    k3 = oc.dot(oc) - sphere.radius**2
    discriminant = k2 * k2 - 4 * k1 * k3
    if discriminant < 0:
        return float('inf'), float('inf')
    sqrt_disc = sqrt(discriminant)
    t1 = (-k2 + sqrt_disc) / (2 * k1)
    t2 = (-k2 - sqrt_disc) / (2 * k1)
    return t1, t2

def intersect_ray_triangle(origin, direction, triangle):
    """Möller–Trumbore algorithm."""
    epsilon = 1e-6
    edge1 = triangle.v1.sub(triangle.v0)
    edge2 = triangle.v2.sub(triangle.v0)
    h = direction.cross(edge2)
    a = edge1.dot(h)
    if abs(a) < epsilon:
        return float('inf')
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
    return t if t > EPSILON else float('inf')

def intersect_ray_cylinder(origin, direction, cylinder):
    """Compute intersection of a ray with a finite cylinder (sides and caps)."""
    d = direction
    o = origin
    b = cylinder.base
    v = cylinder.axis
    r = cylinder.radius

    # --- Side Intersection ---
    d_dot_v = d.dot(v)
    d_proj = d.sub(v.mul(d_dot_v))
    w = o.sub(b)
    w_dot_v = w.dot(v)
    w_proj = w.sub(v.mul(w_dot_v))
    a = d_proj.dot(d_proj)
    b_quad = 2 * d_proj.dot(w_proj)
    c_val = w_proj.dot(w_proj) - r * r

    t_side = float('inf')
    discriminant = b_quad * b_quad - 4 * a * c_val
    if abs(a) > EPSILON and discriminant >= 0:
        sqrt_disc = sqrt(discriminant)
        t1 = (-b_quad + sqrt_disc) / (2 * a)
        t2 = (-b_quad - sqrt_disc) / (2 * a)
        for t in [t1, t2]:
            if t > EPSILON:
                P = o.add(d.mul(t))
                proj = P.sub(b).dot(v)
                if 0 <= proj <= cylinder.height:
                    t_side = min(t_side, t)
    # --- Cap Intersections ---
    t_cap = float('inf')
    # Bottom cap:
    if abs(d.dot(v)) > EPSILON:
        t_bottom = (cylinder.base.sub(o)).dot(v) / d.dot(v)
        if t_bottom > EPSILON:
            P_bottom = o.add(d.mul(t_bottom))
            if P_bottom.sub(cylinder.base).sub(v.mul(P_bottom.sub(cylinder.base).dot(v))).length() <= r:
                t_cap = min(t_cap, t_bottom)
    # Top cap:
    top_center = cylinder.base.add(v.mul(cylinder.height))
    if abs(d.dot(v)) > EPSILON:
        t_top = (top_center.sub(o)).dot(v) / d.dot(v)
        if t_top > EPSILON:
            P_top = o.add(d.mul(t_top))
            if P_top.sub(top_center).sub(v.mul(P_top.sub(top_center).dot(v))).length() <= r:
                t_cap = min(t_cap, t_top)

    t_final = min(t_side, t_cap)
    return t_final if t_final != float('inf') else float('inf')

# ------------------------------------------------------------
# OBJ Loader for the Bunny
# ------------------------------------------------------------

def load_obj(filename, color, specular, reflective):
    """Load a Wavefront OBJ file and return a list of Triangle objects."""
    vertices = []
    tris = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('v '):
                parts = line.split()
                try:
                    x = float(parts[1])
                    y = float(parts[2])
                    z = float(parts[3])
                except Exception as e:
                    print("Error parsing vertex line:", line)
                    continue
                vertices.append(Vec(x, y, z))
            elif line.startswith('f '):
                parts = line.split()
                try:
                    idx0 = int(parts[1].split('/')[0]) - 1
                    idx1 = int(parts[2].split('/')[0]) - 1
                    idx2 = int(parts[3].split('/')[0]) - 1
                except Exception as e:
                    print("Error parsing face line:", line)
                    continue
                try:
                    v0 = vertices[idx0]
                    v1 = vertices[idx1]
                    v2 = vertices[idx2]
                except IndexError as e:
                    print("Index error in face line:", line)
                    continue
                tris.append(Triangle(v0, v1, v2, color, specular, reflective))
    return tris

# ------------------------------------------------------------
# Intersection, Lighting, and Ray Tracing Functions
# ------------------------------------------------------------

def closest_intersection(origin, direction, t_min, t_max):
    closest_t = float('inf')
    closest_obj = None

    # Check spheres.
    for sphere in spheres:
        t1, t2 = intersect_ray_sphere(origin, direction, sphere)
        if t_min < t1 < t_max and t1 < closest_t:
            closest_t = t1
            closest_obj = sphere
        if t_min < t2 < t_max and t2 < closest_t:
            closest_t = t2
            closest_obj = sphere

    # Check bunny triangles.
    if triangles and bunny_bbox_min is not None and bunny_bbox_max is not None:
        if ray_intersect_aabb(origin, direction, bunny_bbox_min, bunny_bbox_max):
            for triangle in triangles:
                t = intersect_ray_triangle(origin, direction, triangle)
                if t_min < t < t_max and t < closest_t:
                    closest_t = t
                    closest_obj = triangle
    else:
        for triangle in triangles:
            t = intersect_ray_triangle(origin, direction, triangle)
            if t_min < t < t_max and t < closest_t:
                closest_t = t
                closest_obj = triangle

    # Check cylinders.
    for cylinder in cylinders:
        t = intersect_ray_cylinder(origin, direction, cylinder)
        if t_min < t < t_max and t < closest_t:
            closest_t = t
            closest_obj = cylinder

    return (closest_obj, closest_t) if closest_obj is not None else None

def compute_lighting(point, normal, view, specular):
    intensity = 0.0
    for light in lights:
        if isinstance(light, AmbientLight):
            intensity += light.intensity
        else:
            if isinstance(light, PointLight):
                L = light.position.sub(point)
                t_max = 1.0
            elif isinstance(light, DirectionalLight):
                L = light.direction
                t_max = float('inf')
            else:
                continue
            if closest_intersection(point, L, EPSILON, t_max) is not None:
                continue
            n_dot_l = normal.dot(L)
            if n_dot_l > 0:
                intensity += light.intensity * n_dot_l / (normal.length() * L.length())
            if specular != -1:
                R = normal.mul(2 * n_dot_l).sub(L)
                r_dot_v = R.dot(view)
                if r_dot_v > 0:
                    intensity += light.intensity * (r_dot_v / (R.length() * view.length())) ** specular
    return intensity

def reflect_ray(incident, normal):
    return normal.mul(2 * incident.dot(normal)).sub(incident)

def trace_ray(origin, direction, t_min, t_max, depth):
    intersection = closest_intersection(origin, direction, t_min, t_max)
    if intersection is None:
        return background_color
    closest_obj, closest_t = intersection
    point = origin.add(direction.mul(closest_t))

    # Compute normal.
    if isinstance(closest_obj, Sphere):
        normal = point.sub(closest_obj.center).normalize()
    elif isinstance(closest_obj, Triangle):
        normal = closest_obj.normal
    elif isinstance(closest_obj, Cylinder):
        v = closest_obj.axis
        proj = point.sub(closest_obj.base).dot(v)
        if 0 < proj < closest_obj.height:
            point_on_axis = closest_obj.base.add(v.mul(proj))
            normal = point.sub(point_on_axis).normalize()
        else:
            normal = v if proj > closest_obj.height else v.mul(-1)
    else:
        normal = Vec(0, 0, 0)

    view = direction.mul(-1)
    lighting = compute_lighting(point, normal, view, closest_obj.specular)
    local_color = closest_obj.color.mul(lighting)
    final_color = local_color

    if closest_obj.reflective > 0 and depth > 0:
        reflected_ray = reflect_ray(view, normal).normalize()
        reflected_color = trace_ray(point, reflected_ray, EPSILON, float('inf'), depth - 1)
        final_color = final_color.mul(1 - closest_obj.reflective).add(reflected_color.mul(closest_obj.reflective))

    if hasattr(closest_obj, 'transparency') and closest_obj.transparency > 0 and depth > 0:
        # For our cylinder we simulate refraction.
        n_air = 1.0
        n_cyl = 1.5
        if direction.dot(normal) < 0:
            refracted = refract_ray(direction, normal, n_air, n_cyl)
        else:
            refracted = refract_ray(direction, normal.mul(-1), n_cyl, n_air)
        if refracted is None:
            transmitted_color = Color(0, 0, 0)
        else:
            transmitted_color = trace_ray(point, refracted, EPSILON, float('inf'), depth - 1)
        final_color = final_color.mul(1 - closest_obj.transparency).add(transmitted_color.mul(closest_obj.transparency))

    return final_color

# ------------------------------------------------------------
# Rendering Function
# ------------------------------------------------------------

def render_scene():
    img = Image.new("RGB", (WIDTH, HEIGHT))
    pixels = img.load()
    for px in range(-WIDTH // 2, WIDTH // 2):
        for py in range(-HEIGHT // 2, HEIGHT // 2):
            direction = canvas_to_viewport(px, py).normalize()
            color = trace_ray(camera_position, direction, 1.0, float('inf'), RECURSION_DEPTH)
            fx = px + WIDTH // 2
            fy = HEIGHT // 2 - py - 1
            r = max(min(int(color.r), 255), 0)
            g = max(min(int(color.g), 255), 0)
            b = max(min(int(color.b), 255), 0)
            pixels[fx, fy] = (r, g, b)
    return img

# ------------------------------------------------------------
# Main: Scene Setup, Bunny Loading, Bunny Bounding Box, and Rendering
# ------------------------------------------------------------

def main():
    global bunny_bbox_min, bunny_bbox_max

    # Load the Stanford Bunny from an OBJ file.
    try:
        bunny_triangles = load_obj("bunny.obj",
                                   color=Color(255, 255, 255),  # White bunny.
                                   specular=10,
                                   reflective=0)
        # Adjust bunny transformation so that it overlaps the cylinder.
        bunny_scale = 3.5
        bunny_translation = Vec(-0.5, -1, 5)  # Adjusted translation: moves bunny rightward.
        for tri in bunny_triangles:
            tri.v0 = tri.v0.mul(bunny_scale).add(bunny_translation)
            tri.v1 = tri.v1.mul(bunny_scale).add(bunny_translation)
            tri.v2 = tri.v2.mul(bunny_scale).add(bunny_translation)
            tri.edge1 = tri.v1.sub(tri.v0)
            tri.edge2 = tri.v2.sub(tri.v0)
            tri.normal = tri.edge1.cross(tri.edge2).normalize()
        triangles.extend(bunny_triangles)
    except Exception as e:
        print("Error loading bunny.obj:", e)

    # Compute bunny bounding box.
    if triangles:
        min_x = min_y = min_z = float('inf')
        max_x = max_y = max_z = -float('inf')
        for tri in triangles:
            for v in [tri.v0, tri.v1, tri.v2]:
                min_x = min(min_x, v.x)
                min_y = min(min_y, v.y)
                min_z = min(min_z, v.z)
                max_x = max(max_x, v.x)
                max_y = max(max_y, v.y)
                max_z = max(max_z, v.z)
        bunny_bbox_min = Vec(min_x, min_y, min_z)
        bunny_bbox_max = Vec(max_x, max_y, max_z)

    image = render_scene()
    image.save("assignment_4_output.png")
    print("Render complete. Saved to assignment_4_output.png")

if __name__ == "__main__":
    main()
