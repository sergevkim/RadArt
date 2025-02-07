import numpy as np
from scipy.spatial import KDTree
from read_and_prepare_files import RadarPoint, LidarPoint, Point, Data
from collections import defaultdict

class Grid():
    def __init__(self, data: list[Point], row_num: int = 100, col_num: int = 100, l_border: float = -130,
                 r_border: float = 130, bottom_border: float = -130, top_border: float = 130):
        self.row_num = row_num
        self.col_num = col_num
        
        self.l_border = l_border
        self.r_border = r_border
        self.top_border = top_border
        self.bottom_border = bottom_border
        
        self.data = defaultdict(list)
        self.size = len(data)
        for point in data:
            x = point.x
            y = point.y
            if (x - l_border) * (x - r_border) >= 0 or (y - top_border) * (y - bottom_border) >= 0:
                continue
            i = int(col_num * (x - l_border) / (r_border - l_border))
            j = int(row_num * (y - bottom_border) / (top_border - bottom_border))

            self.data[i,j].append(point)
            
    def count(self, i: int, j: int) -> int:
        return len(self.data[i, j])
    
    def size() -> int:
        return self.size
        
    def density(self, i, j):
        return self.count(i, j) / self.size if self.size > 0 else 0
        
def DensityMetric(lid_cloud: list[Point], rad_cloud: list[Point], size: int) -> float:
    grid_1 = Grid(lid_cloud, size, size)
    grid_2 = Grid(rad_cloud, size, size)
    s = 0
    keys = grid_1.data.keys() | grid_2.data.keys()
    for key in keys:
        i, j = key
        s += (grid_1.density(i, j) - grid_2.density(i, j)) ** 2
    return s ** 0.5 / len(keys)

def from_point_to_pair(points: list[Point]):
    return [(p.x, p.y) for p in points]

def find_nearest_lidar_points(lidar_points: list[(float, float)], radar_points: list[(float, float)]):
    #Находит ближайшую лидарную точку для каждой радарной точки на плоскости и расстояние до нее.
    lid_points = from_point_to_pair(lidar_points)
    rad_points = from_point_to_pair(radar_points)
    lidar_tree = KDTree(lid_points)  
    distances, indices = lidar_tree.query(rad_points) 
    return distances, [lidar_points[i] for i in indices]
    
def NearestPointMetric(lid_cloud: list[Point], rad_cloud: list[Point]) -> float:
    distances = find_nearest_lidar_points(lid_cloud, rad_cloud)[0]
    return ((distances ** 2).sum() / len(rad_cloud)) ** 0.5
                                     