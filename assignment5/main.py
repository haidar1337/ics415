from PIL import Image
import sys, os, math


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from assignment5.bvh import BVHNode
from assignment5.triangle import Triangle
import assignment1.vec
import assignment1.color
import assignment2.light

WIDTH = 500
HEIGHT = 500
viewport_size = 1.0
projection_plane_z = 1.0

camera_position = assignment1.vec.Vec(0, 0, 0)

camera_rotation = [
    [0.7071, 0, -0.7071],
    [0,      1,  0],
    [0.7071, 0,  0.7071]
]

background_color = assignment1.color.Color(0, 0, 0)

EPSILON = 0.001
RECURSION_DEPTH = 3

triangles = []

lights = [
    assignment2.light.AmbientLight(intensity=0.2),
    assignment2.light.PointLight(intensity=0.6, position=assignment1.vec.Vec(2, 1, 0)),
    assignment2.light.DirectionalLight(intensity=0.2, direction=assignment1.vec.Vec(1, 4, 4))
]


def canvas_to_viewport(x, y):
    """
    Converts canvas (pixel) coordinates (with the origin at the center)
    into viewport coordinates.
    """
    return assignment1.vec.Vec(
        x * viewport_size / WIDTH,
        y * viewport_size / HEIGHT,
        projection_plane_z
    )


def multiply_mv(mat, vec):
    x, y, z = vec.x, vec.y, vec.z
    rx = mat[0][0] * x + mat[0][1] * y + mat[0][2] * z
    ry = mat[1][0] * x + mat[1][1] * y + mat[1][2] * z
    rz = mat[2][0] * x + mat[2][1] * y + mat[2][2] * z
    return assignment1.vec.Vec(rx, ry, rz)


def intersect_ray_triangle(origin, direction, triangle):
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
    if t > EPSILON:
        return t
    else:
        return float('inf')




def load_obj(filename, color, specular, reflective):
    """
    Loads an OBJ file and returns a list of Triangle objects.
    Assumes that the OBJ faces are triangles.
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
                idx0 = int(parts[1].split('/')[0]) - 1
                idx1 = int(parts[2].split('/')[0]) - 1
                idx2 = int(parts[3].split('/')[0]) - 1
                v0 = vertices[idx0]
                v1 = vertices[idx1]
                v2 = vertices[idx2]
                tris.append(Triangle(v0, v1, v2, color, specular, reflective))
    return tris





def compute_bbox_for_triangles(triangles):
    """Computes an axis-aligned bounding box for a list of triangles."""
    first = triangles[0]
    min_x = min(first.v0.x, first.v1.x, first.v2.x)
    min_y = min(first.v0.y, first.v1.y, first.v2.y)
    min_z = min(first.v0.z, first.v1.z, first.v2.z)
    max_x = max(first.v0.x, first.v1.x, first.v2.x)
    max_y = max(first.v0.y, first.v1.y, first.v2.y)
    max_z = max(first.v0.z, first.v1.z, first.v2.z)
    for tri in triangles[1:]:
        min_x = min(min_x, tri.v0.x, tri.v1.x, tri.v2.x)
        min_y = min(min_y, tri.v0.y, tri.v1.y, tri.v2.y)
        min_z = min(min_z, tri.v0.z, tri.v1.z, tri.v2.z)
        max_x = max(max_x, tri.v0.x, tri.v1.x, tri.v2.x)
        max_y = max(max_y, tri.v0.y, tri.v1.y, tri.v2.y)
        max_z = max(max_z, tri.v0.z, tri.v1.z, tri.v2.z)
    return assignment1.vec.Vec(min_x, min_y, min_z), assignment1.vec.Vec(max_x, max_y, max_z)


def build_bvh(triangles, max_triangles_per_leaf=4):
    """
    Recursively builds a BVH (Bounding Volume Hierarchy) for the list of triangles.
    """
    if len(triangles) <= max_triangles_per_leaf:
        bbox_min, bbox_max = compute_bbox_for_triangles(triangles)
        return BVHNode(bbox_min, bbox_max, triangles=triangles)
    bbox_min, bbox_max = compute_bbox_for_triangles(triangles)
    extent = bbox_max.sub(bbox_min)
    if extent.x >= extent.y and extent.x >= extent.z:
        axis = 'x'
    elif extent.y >= extent.x and extent.y >= extent.z:
        axis = 'y'
    else:
        axis = 'z'
    triangles.sort(key=lambda tri: getattr(tri.v0.add(tri.v1).add(tri.v2).div(3), axis))
    mid = len(triangles) // 2
    left_child = build_bvh(triangles[:mid], max_triangles_per_leaf)
    right_child = build_bvh(triangles[mid:], max_triangles_per_leaf)
    combined_min = assignment1.vec.Vec(
        min(left_child.bbox_min.x, right_child.bbox_min.x),
        min(left_child.bbox_min.y, right_child.bbox_min.y),
        min(left_child.bbox_min.z, right_child.bbox_min.z)
    )
    combined_max = assignment1.vec.Vec(
        max(left_child.bbox_max.x, right_child.bbox_max.x),
        max(left_child.bbox_max.y, right_child.bbox_max.y),
        max(left_child.bbox_max.z, right_child.bbox_max.z)
    )
    return BVHNode(combined_min, combined_max, left=left_child, right=right_child)


def intersect_ray_aabb(origin, direction, bbox_min, bbox_max, t_min, t_max):
    """
    Checks whether a ray intersects an axis-aligned bounding box using the slab method.
    """
    for axis in ['x', 'y', 'z']:
        o = getattr(origin, axis)
        d = getattr(direction, axis)
        min_val = getattr(bbox_min, axis)
        max_val = getattr(bbox_max, axis)
        if abs(d) < EPSILON:
            if o < min_val or o > max_val:
                return False
        else:
            invD = 1.0 / d
            t0 = (min_val - o) * invD
            t1 = (max_val - o) * invD
            if t0 > t1:
                t0, t1 = t1, t0
            t_min = max(t_min, t0)
            t_max = min(t_max, t1)
            if t_max < t_min:
                return False
    return True


def bvh_intersect(node, origin, direction, t_min, t_max):
    """
    Recursively traverses the BVH to find the closest triangle intersected by the ray.
    Returns a tuple (triangle, t) if an intersection is found; otherwise, None.
    """
    if not intersect_ray_aabb(origin, direction, node.bbox_min, node.bbox_max, t_min, t_max):
        return None
    hit_obj = None
    closest_t = float('inf')
    if node.is_leaf:
        for tri in node.triangles:
            t = intersect_ray_triangle(origin, direction, tri)
            if t_min < t < t_max and t < closest_t:
                closest_t = t
                hit_obj = tri
    else:
        hit_left = bvh_intersect(node.left, origin, direction, t_min, t_max)
        hit_right = bvh_intersect(node.right, origin, direction, t_min, t_max)
        if hit_left is not None:
            obj_left, t_left = hit_left
            if t_left < closest_t:
                closest_t = t_left
                hit_obj = obj_left
        if hit_right is not None:
            obj_right, t_right = hit_right
            if t_right < closest_t:
                closest_t = t_right
                hit_obj = obj_right
    if hit_obj is not None:
        return (hit_obj, closest_t)
    return None


def closest_intersection(origin, direction, t_min, t_max):
    """
    Finds the closest intersecting triangle (if any) using the BVH.
    """
    return bvh_intersect(bvh_root, origin, direction, t_min, t_max)


def compute_lighting(point, normal, view, specular):
    """
    Computes the lighting at a point using ambient, diffuse, and specular components.
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
            # Shadow check.
            if closest_intersection(point, L, EPSILON, t_max) is not None:
                continue
            # Diffuse lighting.
            n_dot_l = normal.dot(L)
            if n_dot_l > 0:
                intensity += light.intensity * n_dot_l / (normal.length() * L.length())
            # Specular lighting.
            if specular != -1:
                R = normal.mul(2 * n_dot_l).sub(L)
                r_dot_v = R.dot(view)
                if r_dot_v > 0:
                    intensity += light.intensity * (r_dot_v / (R.length() * view.length())) ** specular
    return intensity


def reflect_ray(incident, normal):
    """
    Computes the reflection of an incident ray with respect to a surface normal.
    """
    return normal.mul(2 * incident.dot(normal)).sub(incident)


def trace_ray(origin, direction, t_min, t_max, depth):
    """
    Traces a ray into the scene. If an intersection is found, it computes local lighting
    and recursively computes reflections.
    """
    intersection = closest_intersection(origin, direction, t_min, t_max)
    if intersection is None:
        return background_color

    closest_obj, closest_t = intersection
    point = origin.add(direction.mul(closest_t))
    normal = closest_obj.normal
    view = direction.mul(-1)
    lighting = compute_lighting(point, normal, view, closest_obj.specular)
    local_color = closest_obj.color.mul(lighting)

    if closest_obj.reflective <= 0 or depth <= 0:
        return local_color

    reflected_ray = reflect_ray(view, normal)
    reflected_color = trace_ray(point, reflected_ray, EPSILON, float('inf'), depth - 1)
    return local_color.mul(1 - closest_obj.reflective).add(reflected_color.mul(closest_obj.reflective))


def render_scene():
    """
    Renders the scene pixel-by-pixel and returns a PIL Image.
    """
    img = Image.new("RGB", (WIDTH, HEIGHT))
    pixels = img.load()

    for px in range(-WIDTH // 2, WIDTH // 2):
        for py in range(-HEIGHT // 2, HEIGHT // 2):
            direction = canvas_to_viewport(px, py)
            # direction = multiply_mv(camera_rotation, direction)
            color = trace_ray(camera_position, direction, 1.0, float('inf'), RECURSION_DEPTH)

            fx = px + WIDTH // 2
            fy = HEIGHT // 2 - py - 1
            r = max(min(int(color.r), 255), 0)
            g = max(min(int(color.g), 255), 0)
            b = max(min(int(color.b), 255), 0)
            pixels[fx, fy] = (r, g, b)
    return img


if __name__ == "__main__":
    try:
        bunny_triangles = load_obj("bunny.obj",
                                   color=assignment1.color.Color(255, 255, 255),
                                   specular=10,
                                   reflective=0.2)
        bunny_scale = 15.0
        bunny_translation = assignment1.vec.Vec(0, -1.5, 4)
        for tri in bunny_triangles:
            tri.v0 = tri.v0.mul(bunny_scale).add(bunny_translation)
            tri.v1 = tri.v1.mul(bunny_scale).add(bunny_translation)
            tri.v2 = tri.v2.mul(bunny_scale).add(bunny_translation)
            tri.edge1 = tri.v1.sub(tri.v0)
            tri.edge2 = tri.v2.sub(tri.v0)
            tri.normal = tri.edge1.cross(tri.edge2).normalize()
        triangles.extend(bunny_triangles)
        bvh_root = build_bvh(triangles)
    except Exception as e:
        print("Error loading bunny.obj:", e)
        sys.exit(1)

    image = render_scene()
    image.save("bunny.png")
