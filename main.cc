#include "color.h"
#include "ray.h"
#include "vec3.h"

#include <iostream>
#include <cmath>
#include <utility>    

struct sphere {
    double radius;
    color  col;
    point3 center;
};

std::pair<double, double> hit_sphere(const point3& center, double radius, const ray& r) {
    vec3 oc = center - r.origin();
    auto a = dot(r.direction(), r.direction());
    auto b = 2.0 * dot(r.direction(), oc);
    auto c = dot(oc, oc) - radius*radius;
    auto discriminant = b*b - 4*a*c;
    if (discriminant < 0) {
        return {INFINITY, INFINITY};
    }

    double sqrt_disc = std::sqrt(discriminant);
    double t1 = (-b + sqrt_disc) / (2*a);
    double t2 = (-b - sqrt_disc) / (2*a);

    return {t1, t2};
}

// Returns the color of whatever the ray hits (or white background if it hits nothing)
color ray_color(const ray& r) {
    double t_min = 0.001;     // a tiny epsilon
    double t_max = INFINITY;

    sphere spheres[] = {
        {1.0, color(1, 0, 0), point3(0, 1, 3)}, 
        {1.0, color(0, 1, 0), point3(-2, 0, 4)},
        {1.0, color(0, 0, 1), point3( 2, 0, 4)}
    };

    double closest_t = INFINITY;
    sphere* closest_sphere = nullptr;

    for (auto& s : spheres) {
        auto [t1, t2] = hit_sphere(s.center, s.radius, r);

        if (t1 > t_min && t1 < t_max && t1 < closest_t) {
            closest_t      = t1;
            closest_sphere = &s;
        }
        if (t2 > t_min && t2 < t_max && t2 < closest_t) {
            closest_t      = t2;
            closest_sphere = &s;
        }
    }

    // Return sphere color if we hit one, or white if we missed them all
    if (closest_sphere) {
        return closest_sphere->col;
    } else {
        return color(1, 1, 1);
    }
}

int main() {

    int image_width = 400;
    int image_height = 400;  

    // Camera 
    double focal_length    = 1.0;
    double viewport_height = 1.0;
    double viewport_width  = 1.0; 
    point3 camera_center   = point3(0, 0, 0);

    auto viewport_u = vec3(viewport_width, 0, 0);
    auto viewport_v = vec3(0, -viewport_height, 0);

    auto pixel_delta_u = viewport_u / (double)image_width;
    auto pixel_delta_v = viewport_v / (double)image_height;

    auto viewport_upper_left = camera_center
                             - vec3(0, 0, focal_length)
                             - 0.5*viewport_u
                             - 0.5*viewport_v;

    auto pixel00_loc = viewport_upper_left + 0.5*(pixel_delta_u + pixel_delta_v);

    // Output header
    std::cout << "P3\n" << image_width << " " << image_height << "\n255\n";

    for (int j = 0; j < image_height; j++) {
        for (int i = 0; i < image_width; i++) {
            auto pixel_center = pixel00_loc 
                              + i*pixel_delta_u 
                              + j*pixel_delta_v;

            auto ray_direction = pixel_center - camera_center;
            ray r(camera_center, ray_direction);

            color pixel_color = ray_color(r);
            write_color(std::cout, pixel_color);
        }
    }
}
