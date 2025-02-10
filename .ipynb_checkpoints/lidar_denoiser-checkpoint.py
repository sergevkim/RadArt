import numpy as np
import random
from typing import List
from read_and_prepare_files import LidarPoint

def fit_plane(p1, p2, p3):

     #Построение плоскости по трем точкам
    
    v1 = np.array([p2.x - p1.x, p2.y - p1.y, p2.z - p1.z])    
    v2 = np.array([p3.x - p1.x, p3.y - p1.y, p3.z - p1.z])
    normal = np.cross(v1, v2)
    norm = np.linalg.norm(normal)
    if norm < 1e-6:
        return None
    normal = normal / norm
    d = -np.dot(normal, [p1.x, p1.y, p1.z])
    return (*normal, d)

def plane_distance(point, plane):

     #Расчет расстояния от точки до плоскости
    
    a, b, c, d = plane       
    return abs(a * point.x + b * point.y + c * point.z + d) / np.sqrt(a**2 + b**2 + c**2)

def local_ransac(points: List[LidarPoint], num_iterations: int, distance_threshold: float, min_plane_points: int) -> List[LidarPoint]:

    #Локальный алгоритм
    
    best_plane = None                                      
    best_inliers = []

    for _ in range(num_iterations):
        try:
            sample = random.sample(points, 3)
        except ValueError:
            continue

        plane = fit_plane(*sample)
        if plane is None:
            continue

        a, b, c, d = plane
        if c < 0:
            a, b, c, d = -a, -b, -c, -d

        inliers = []
        for p in points:
            if plane_distance(p, (a, b, c, d)) < distance_threshold:
                inliers.append(p)

        if len(inliers) > len(best_inliers) and len(inliers) >= min_plane_points:
            best_plane = (a, b, c, d)
            best_inliers = inliers

    if best_plane is not None:
        filtered = [p for p in points if plane_distance(p, best_plane) >= distance_threshold]
        return filtered
    return points

def grid_segmentation(points: List[LidarPoint], grid_size: float) -> dict:       

    #Разбиение точек на прямоугольные сегменты
    segments = {}

    for p in points:
        x_bin = int(p.x // grid_size)
        y_bin = int(p.y // grid_size)
        key = (x_bin, y_bin)
        if key not in segments:
            segments[key] = []
        segments[key].append(p)

    return segments

def noise_filtering (points: List[LidarPoint]) -> List[LidarPoint]:
    
    #Основная функция для фильтрации асфальта с сегментацией
    
    GRID_SIZE = 7.5  # Размер ячейки сетки в метрах

    # Параметры RANSAC для каждого сегмента
    RANSAC_ITERATIONS = 50
    DISTANCE_THRESHOLD = 0.045
    MIN_PLANE_POINTS = 50


    prefiltered = [p for p in points if p.z > -0.2]
    segments = grid_segmentation(prefiltered, GRID_SIZE)
    filtered_points = []
    
    for segment_key, segment_points in segments.items():
        if len(segment_points) < MIN_PLANE_POINTS:
            filtered_points.extend(segment_points)
            continue

        filtered_segment = local_ransac(segment_points, RANSAC_ITERATIONS, DISTANCE_THRESHOLD, MIN_PLANE_POINTS)
        filtered_points.extend(filtered_segment)

    filtered_points = [p for p in filtered_points if p.z > -0.1]

    return filtered_points