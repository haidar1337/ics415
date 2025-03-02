
#ifdef GL_ES
precision mediump float;
#endif

#define MAX_DEPTH 3
#define EPSILON 0.001

vec3 backgroundColor = vec3(135.0, 206.0, 235.0) / 255.0;

float rand(vec2 co) {
    return fract(sin(dot(co, vec2(12.9898,78.233))) * 43758.5453);
}

float intersectSphere(vec3 ro, vec3 rd, vec3 center, float radius) {
    vec3 oc = ro - center;
    float a = dot(rd, rd);
    float b = 2.0 * dot(oc, rd);
    float c = dot(oc, oc) - radius * radius;
    float discriminant = b * b - 4.0 * a * c;
    if(discriminant < 0.0) return -1.0;
    float sqrtDisc = sqrt(discriminant);
    float t1 = (-b - sqrtDisc) / (2.0 * a);
    if(t1 > EPSILON) return t1;
    float t2 = (-b + sqrtDisc) / (2.0 * a);
    if(t2 > EPSILON) return t2;
    return -1.0;
}

struct Hit {
    float t;
    vec3 center;
    float radius;
    vec3 color;
    float specular;
    float reflective;
    bool hit;
};

struct Light {
    int type;
    float intensity;
    vec3 position;  // used for point light
    vec3 direction; // used for directional light
};

const int NLIGHTS = 3;
Light lights[NLIGHTS];

float computeLighting(vec3 point, vec3 normal, vec3 view, float specular) {
    float intensity = 0.0;
    // Ambient light
    intensity += lights[0].intensity;
    
    // For each non–ambient light:
    for (int i = 1; i < NLIGHTS; i++) {
        Light light = lights[i];
        vec3 L;
        float t_max;
        if (light.type == 1) { // Point light
            L = light.position - point;
            t_max = 1.0;
        } else if (light.type == 2) { // Directional light
            L = light.direction;
            t_max = 1e9;
        }
        
        // Shadow check: cast a ray from the point toward the light
        vec3 shadowOrig = point + normal * EPSILON;
        bool inShadow = false;
        float t = intersectSphere(shadowOrig, normalize(L), vec3(0.0, -1000.0, 0.0), 1000.0);
        if (t > EPSILON && t < t_max) { inShadow = true; }
        
        for (int a = -11; a <= 11; a++) {
            for (int b = -11; b <= 11; b++) {
                vec2 seed = vec2(float(a), float(b));
                float r1 = rand(seed);
                float r2 = rand(seed + 1.0);
                vec3 center = vec3(float(a) + 0.9 * r1, 0.2, float(b) + 0.9 * r2);
                if (length(center - vec3(4.0, 0.2, 0.0)) > 0.9) {
                    float t_tmp = intersectSphere(shadowOrig, normalize(L), center, 0.2);
                    if (t_tmp > EPSILON && t_tmp < t_max) { inShadow = true; break; }
                }
            }
            if (inShadow) break;
        }
        
        t = intersectSphere(shadowOrig, normalize(L), vec3(0.0, 1.0, 0.0), 1.0);
        if (t > EPSILON && t < t_max) inShadow = true;
        t = intersectSphere(shadowOrig, normalize(L), vec3(-4.0, 1.0, 0.0), 1.0);
        if (t > EPSILON && t < t_max) inShadow = true;
        t = intersectSphere(shadowOrig, normalize(L), vec3(4.0, 1.0, 0.0), 1.0);
        if (t > EPSILON && t < t_max) inShadow = true;
        
        if (inShadow) continue;
        
        // Diffuse component
        float n_dot_l = dot(normal, normalize(L));
        if (n_dot_l > 0.0)
            intensity += light.intensity * n_dot_l;
        
        // Specular component
        if (specular >= 0.0) {
            vec3 R = reflect(-normalize(L), normal);
            float r_dot_v = dot(R, view);
            if (r_dot_v > 0.0)
                intensity += light.intensity * pow(r_dot_v, specular);
        }
    }
    return intensity;
}

Hit sceneHit(vec3 ro, vec3 rd) {
    Hit best;
    best.t = 1e9;
    best.hit = false;
    float t;
    
    // Ground sphere (a large sphere below the scene)
    t = intersectSphere(ro, rd, vec3(0.0, -1000.0, 0.0), 1000.0);
    if (t > EPSILON && t < best.t) {
        best.t = t;
        best.center = vec3(0.0, -1000.0, 0.0);
        best.radius = 1000.0;
        best.color = vec3(0.5); // grey
        best.specular = -1.0;
        best.reflective = 0.0;
        best.hit = true;
    }
    
    // Grid of small random spheres
    for (int a = -11; a <= 11; a++) {
        for (int b = -11; b <= 11; b++) {
            vec2 seed = vec2(float(a), float(b));
            float r1 = rand(seed);
            float r2 = rand(seed + 1.0);
            vec3 center = vec3(float(a) + 0.9 * r1, 0.2, float(b) + 0.9 * r2);
            if (length(center - vec3(4.0, 0.2, 0.0)) > 0.9) {
                float radius = 0.2;
                float choose = rand(seed + 2.0);
                vec3 col;
                float spec;
                float refl;
                if (choose < 0.8) {
                    // Diffuse material
                    col = vec3(rand(seed+3.0)*rand(seed+4.0),
                               rand(seed+5.0)*rand(seed+6.0),
                               rand(seed+7.0)*rand(seed+8.0));
                    spec = -1.0;
                    refl = 0.0;
                } else if (choose < 0.95) {
                    // Metal material
                    col = vec3(0.5 + 0.5 * rand(seed+9.0),
                               0.5 + 0.5 * rand(seed+10.0),
                               0.5 + 0.5 * rand(seed+11.0));
                    spec = 250.0;
                    refl = 0.8;
                } else {
                    // Dielectric (glass) material
                    col = vec3(1.0);
                    spec = 500.0;
                    refl = 0.9;
                }
                t = intersectSphere(ro, rd, center, radius);
                if (t > EPSILON && t < best.t) {
                    best.t = t;
                    best.center = center;
                    best.radius = radius;
                    best.color = col;
                    best.specular = spec;
                    best.reflective = refl;
                    best.hit = true;
                }
            }
        }
    }
    
    // Three main spheres
    // Sphere at (0,1,0) — glass/dielectric.
    t = intersectSphere(ro, rd, vec3(0.0, 1.0, 0.0), 1.0);
    if (t > EPSILON && t < best.t) {
        best.t = t;
        best.center = vec3(0.0, 1.0, 0.0);
        best.radius = 1.0;
        best.color = vec3(1.0);
        best.specular = 500.0;
        best.reflective = 0.9;
        best.hit = true;
    }
    // Sphere at (-4,1,0) — diffuse.
    t = intersectSphere(ro, rd, vec3(-4.0, 1.0, 0.0), 1.0);
    if (t > EPSILON && t < best.t) {
        best.t = t;
        best.center = vec3(-4.0, 1.0, 0.0);
        best.radius = 1.0;
        best.color = vec3(0.4, 0.2, 0.1);
        best.specular = -1.0;
        best.reflective = 0.0;
        best.hit = true;
    }
    // Sphere at (4,1,0) — metal.
    t = intersectSphere(ro, rd, vec3(4.0, 1.0, 0.0), 1.0);
    if (t > EPSILON && t < best.t) {
        best.t = t;
        best.center = vec3(4.0, 1.0, 0.0);
        best.radius = 1.0;
        best.color = vec3(0.7, 0.6, 0.5);
        best.specular = 250.0;
        best.reflective = 1.0;
        best.hit = true;
    }
    
    return best;
}

vec3 traceRay(vec3 ro, vec3 rd) {
    vec3 finalColor = vec3(0.0);
    float reflectance = 1.0;
    
    for (int i = 0; i < MAX_DEPTH; i++) {
        Hit hit = sceneHit(ro, rd);
        if (!hit.hit) {
            finalColor += reflectance * backgroundColor;
            break;
        }
        vec3 hitPoint = ro + rd * hit.t;
        vec3 normal = normalize(hitPoint - hit.center);
        float lighting = computeLighting(hitPoint, normal, -rd, hit.specular);
        vec3 localColor = hit.color * lighting;
        finalColor += reflectance * localColor;
        
        reflectance *= hit.reflective;
        ro = hitPoint + normal * EPSILON; // offset to avoid self–intersection
        rd = reflect(rd, normal);
    }
    return finalColor;
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    // Initialize lights:
    // Ambient light
    lights[0].type = 0; lights[0].intensity = 0.2;
    // Point light at (2,1,0)
    lights[1].type = 1; lights[1].intensity = 0.4; lights[1].position = vec3(2.0, 1.0, 0.0);
    // Directional light with direction (1,4,4)
    lights[2].type = 2; lights[2].intensity = 0.4; lights[2].direction = vec3(1.0, 4.0, 4.0);
    
    // Set up the viewport from the canvas coordinates.
    float vfov = 20.0;
    float viewport_height = 2.0 * tan(radians(vfov) / 2.0);
    float viewport_width = (iResolution.x / iResolution.y) * viewport_height;
    float projection_plane_z = 1.0;
    
    float x = fragCoord.x - iResolution.x / 2.0;
    float y = fragCoord.y - iResolution.y / 2.0;
    vec3 direction = vec3(x * viewport_width / iResolution.x,
                          y * viewport_height / iResolution.y,
                          projection_plane_z);
    
    vec3 camPos = vec3(13.0, 2.0, 3.0);
    vec3 lookat = vec3(0.0, 0.0, 0.0);
    vec3 vup = vec3(0.0, 1.0, 0.0);
    vec3 w = normalize(camPos - lookat);
    vec3 u = normalize(cross(vup, w));
    vec3 v = cross(w, u);
    mat3 camRot = mat3(u, v, -w);
    
    direction = normalize(camRot * direction);
    
    vec3 color = traceRay(camPos, direction);
    
    fragColor = vec4(color, 1.0);
}
