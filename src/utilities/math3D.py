#
import numpy as np


def intersect_ray_sphere(ray_origin, ray_direction, sphere_center, sphere_radius):
    oc = sphere_center - ray_origin
    tca = np.dot(oc, ray_direction)
    d2 = np.dot(oc, oc) - tca * tca
    if d2 > sphere_radius * sphere_radius:
        return None  # No intersection
    thc = np.sqrt(sphere_radius * sphere_radius - d2)
    t0 = tca - thc
    t1 = tca + thc
    if t0 > t1:
        t0, t1 = t1, t0
    if t0 < 0:
        t0 = t1
        if t0 < 0:
            return None
    # Calculate the intersection point
    intersection_point = ray_origin + ray_direction * t0
    return intersection_point

def is_occluded(camera_position, target_position, sphere):
    ray_origin, ray_direction = get_ray(camera_position, target_position)
    intersection_point = intersect_ray_sphere(ray_origin, ray_direction, sphere.center, sphere.radius.km)
    if intersection_point is not None:
        # Calculate vector to the target position and find the intersection point
        vector_to_satellite = np.array(target_position) - ray_origin
        vector_to_intersection = intersection_point - ray_origin

        # Check if the intersection point is closer than the target position
        distance_to_satellite = np.linalg.norm(vector_to_satellite)
        distance_to_intersection = np.linalg.norm(vector_to_intersection)

        return distance_to_intersection < distance_to_satellite
    return False

def get_ray(camera_position, target_position):
    direction = np.array(target_position) - np.array(camera_position)
    normalized_direction = direction / np.linalg.norm(direction)
    return camera_position, normalized_direction

def normalize(vector):
    return vector / np.linalg.norm(vector)
