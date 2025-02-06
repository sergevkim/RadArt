import numpy as np
import random
import json
from typing import List
from read_and_prepare_files import LidarPoint

def filter_asphalt(points: List[LidarPoint]) -> List[LidarPoint]:

    num_iterations = 100 #   количество итераций RANSAC
    distance_threshold = 0.020 #   максимальное расстояние до плоскости для inliers (в метрах)
    min_plane_points = 1000 #   минимальное количество точек для признания плоскости валидной 
    
    def fit_plane(p1, p2, p3):
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
        a, b, c, d = plane
        return abs(a * point.x + b * point.y + c * point.z + d) / np.sqrt(a ** 2 + b ** 2 + c ** 2)

    # Предварительная фильтрация нижнего слоя
    prefiltered = [p for p in points if p.z > -0.2]
    

    best_plane = None
    best_inliers = []
    
    for _ in range(num_iterations):
        # Выбор трех уникальных точек
        try:
            sample = random.sample(prefiltered, 3)
        except ValueError:
            continue
            
        # Проверка на коллинеарность
        plane = fit_plane(*sample)
        if plane is None:
            continue
            
        # Определение направления нормали (должна быть направлена вверх)
        a, b, c, d = plane
        if c < 0:
            a, b, c, d = -a, -b, -c, -d

        # Поиск inliers
        inliers = []
        for p in prefiltered:
            if plane_distance(p, (a, b, c, d)) < distance_threshold:
                inliers.append(p)
                
        # Проверка на лучшую плоскость
        if len(inliers) > len(best_inliers) and len(inliers) >= min_plane_points:
            best_plane = (a, b, c, d)
            best_inliers = inliers
    print(best_plane)
    # Фильтрация исходных точек
    if best_plane is not None:
        a, b, c, d = best_plane
        filtered = [
            p for p in points 
            if plane_distance(p, best_plane) >= distance_threshold
        ]
        return filtered