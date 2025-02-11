from PIL import Image
import sys, os, random, math

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import assignment1.vec
import assignment1.color
import assignment1.sphere
import assignment2.light

WIDTH = 1200
HEIGHT = 675
aspect_ratio = 16 / 9

vfov = 20  

viewport_height = 2 * math.tan(math.radians(vfov) / 2)
viewport_width = aspect_ratio * viewport_height

projection_plane_z = 1.0

camera_position = assignment1.vec.Vec(13, 2, 3)
lookfrom = camera_position
lookat   = assignment1.vec.Vec(0, 0, 0)
vup      = assignment1.vec.Vec(0, 1, 0)

w = lookfrom.sub(lookat).div(lookfrom.sub(lookat).length())
u = vup.cross(w).div(vup.cross(w).length())
v = w.cross(u)

camera_rotation = [
    [u.x,         v.x,         -w.x],
    [u.y,         v.y,         -w.y],
    [u.z,         v.z,         -w.z]
]

lights = [
    assignment2.light.AmbientLight(intensity=0.4),         
    assignment2.light.PointLight(intensity=0.8, position=assignment1.vec.Vec(2, 1, 0)),  
    assignment2.light.DirectionalLight(intensity=0.6, direction=assignment1.vec.Vec(1, 4, 4))  
]

background_color = assignment1.color.Color(135, 206, 235)

#   • For a diffuse (lambertian) material, set specular = -1 and reflective = 0.
#   • For a metal, use a high specular exponent (e.g. 250) and a high reflective factor.
#   • For a dielectric (glass) sphere, we simulate with a white color,
#     high specular exponent and a reflective factor near 0.9.
spheres = []

ground_color = assignment1.color.Color(int(0.5 * 255), int(0.5 * 255), int(0.5 * 255))
spheres.append(
    assignment1.sphere.Sphere(assignment1.vec.Vec(0, -1000, 0), 1000,
                                ground_color, specular=-1, reflective=0)
)

for a in range(-11, 11):
    for b in range(-11, 11):
        choose_mat = random.random()
        center = assignment1.vec.Vec(
            a + 0.9 * random.random(),
            0.2,
            b + 0.9 * random.random()
        )
        if center.sub(assignment1.vec.Vec(4, 0.2, 0)).length() > 0.9:
            if choose_mat < 0.8:
                r = random.random() * random.random()
                g = random.random() * random.random()
                b_val = random.random() * random.random()
                diffuse_color = assignment1.color.Color(
                    int(r * 255), int(g * 255), int(b_val * 255)
                )
                spheres.append(
                    assignment1.sphere.Sphere(center, 0.2, diffuse_color,
                                              specular=-1, reflective=0)
                )
            elif choose_mat < 0.95:
                r = random.uniform(0.5, 1)
                g = random.uniform(0.5, 1)
                b_val = random.uniform(0.5, 1)
                metal_color = assignment1.color.Color(
                    int(r * 255), int(g * 255), int(b_val * 255)
                )
                spheres.append(
                    assignment1.sphere.Sphere(center, 0.2, metal_color,
                                              specular=250, reflective=0.8)
                )
            else:
                spheres.append(
                    assignment1.sphere.Sphere(center, 0.2, assignment1.color.Color(255, 255, 255),
                                              specular=500, reflective=0.9)
                )

spheres.append(
    assignment1.sphere.Sphere(assignment1.vec.Vec(0, 1, 0), 1.0,
                              assignment1.color.Color(255, 255, 255),
                              specular=500, reflective=0.9)
)
spheres.append(
    assignment1.sphere.Sphere(assignment1.vec.Vec(-4, 1, 0), 1.0,
                              assignment1.color.Color(int(0.4 * 255), int(0.2 * 255), int(0.1 * 255)),
                              specular=-1, reflective=0)
)
spheres.append(
    assignment1.sphere.Sphere(assignment1.vec.Vec(4, 1, 0), 1.0,
                              assignment1.color.Color(int(0.7 * 255), int(0.6 * 255), int(0.5 * 255)),
                              specular=250, reflective=1.0)
)

def canvas_to_viewport(x, y):
    """
    Convert 2D canvas coordinates (origin at canvas center) into
    a 3D point on the viewport (with z = projection_plane_z).
    """
    return assignment1.vec.Vec(
        x * viewport_width / WIDTH,
        y * viewport_height / HEIGHT,
        projection_plane_z
    )

def multiply_mv(mat, vec):
    """
    Multiply a 3x3 matrix (list of 3 lists) by a Vec.
    Returns a new Vec.
    """
    rx = mat[0][0] * vec.x + mat[0][1] * vec.y + mat[0][2] * vec.z
    ry = mat[1][0] * vec.x + mat[1][1] * vec.y + mat[1][2] * vec.z
    rz = mat[2][0] * vec.x + mat[2][1] * vec.y + mat[2][2] * vec.z
    return assignment1.vec.Vec(rx, ry, rz)

def intersect_ray_sphere(origin, direction, sphere):
    """
    Computes the intersections (t values) of a ray with a sphere.
    Returns a tuple (t1, t2). If no intersection, returns (inf, inf).
    """
    oc = origin.sub(sphere.center)
    k1 = direction.dot(direction)
    k2 = 2 * oc.dot(direction)
    k3 = oc.dot(oc) - sphere.radius ** 2

    discriminant = k2 * k2 - 4 * k1 * k3
    if discriminant < 0:
        return float('inf'), float('inf')
    sqrt_d = math.sqrt(discriminant)
    t1 = (-k2 + sqrt_d) / (2 * k1)
    t2 = (-k2 - sqrt_d) / (2 * k1)
    return t1, t2

def closest_intersection(origin, direction, t_min, t_max):
    """
    Finds the closest sphere hit by the ray (if any) within (t_min, t_max).
    Returns a tuple (sphere, t) if found, or None otherwise.
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
    Computes the lighting at a point with a given surface normal.
    Considers ambient, diffuse, and specular lighting (if specular != -1).
    Also casts shadow rays toward non-ambient lights.
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

            # Diffuse shading.
            n_dot_l = normal.dot(L)
            if n_dot_l > 0:
                intensity += light.intensity * n_dot_l / (normal.length() * L.length())

            # Specular shading.
            if specular != -1:
                R = normal.mul(2 * n_dot_l).sub(L)
                r_dot_v = R.dot(view)
                if r_dot_v > 0:
                    intensity += light.intensity * (r_dot_v / (R.length() * view.length())) ** specular

    return intensity

def reflect_ray(incident, normal):
    """
    Reflects the incident ray around the given normal.
    Formula: R = 2*(incident dot normal)*normal - incident.
    """
    return normal.mul(2 * incident.dot(normal)).sub(incident)

EPSILON = 0.001
RECURSION_DEPTH = 3

def trace_ray(origin, direction, t_min, t_max, depth):
    """
    Traces a ray into the scene. If it hits an object, computes local color (using
    diffuse and specular lighting) and, if reflective and depth limit not reached,
    recursively computes the reflected color.
    Returns a Color.
    """
    hit = closest_intersection(origin, direction, t_min, t_max)
    if hit is None:
        # Return the light blue background.
        return background_color

    closest_sphere, closest_t = hit
    point = origin.add(direction.mul(closest_t))
    normal = point.sub(closest_sphere.center).div(point.sub(closest_sphere.center).length())
    view = direction.mul(-1)

    lighting = compute_lighting(point, normal, view, closest_sphere.specular)
    local_color = closest_sphere.color.mul(lighting)

    if closest_sphere.reflective <= 0 or depth <= 0:
        return local_color

    reflected_ray = reflect_ray(view, normal)
    reflected_color = trace_ray(point, reflected_ray, EPSILON, float('inf'), depth - 1)
    return local_color.mul(1 - closest_sphere.reflective).add(
        reflected_color.mul(closest_sphere.reflective)
    )

def render_scene():
    """
    Renders the scene scanline-by-scanline and returns a PIL Image.
    For each pixel, a ray is cast from the camera position in a direction computed
    from canvas coordinates (with origin at the center) then transformed by the
    camera rotation matrix.
    """
    img = Image.new("RGB", (WIDTH, HEIGHT))
    pixels = img.load()

    for j in range(HEIGHT):
        for i in range(WIDTH):
            # Convert pixel coordinates (i, j) to canvas coordinates.
            canvas_x = i - WIDTH / 2
            canvas_y = HEIGHT / 2 - j - 1
            direction = canvas_to_viewport(canvas_x, canvas_y)
            direction = multiply_mv(camera_rotation, direction)
            color = trace_ray(camera_position, direction, 1.0, float('inf'), RECURSION_DEPTH)
            r = max(min(int(color.r), 255), 0)
            g = max(min(int(color.g), 255), 0)
            b = max(min(int(color.b), 255), 0)
            pixels[i, j] = (r, g, b)
        print(f"Scanline {j+1}/{HEIGHT} complete", flush=True)
    return img

if __name__ == "__main__":
    image = render_scene()
    image.save("project_output.png")
    print("Rendering complete. Saved as project_output.png")
