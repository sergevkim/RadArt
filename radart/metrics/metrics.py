import numpy as np
from scipy.spatial import KDTree
from preprocessing import RadarPoint, LidarPoint, Point, Data, apply_gaussian_kernel_to_mult_radar_points
from collections import defaultdict
from lidar_denoiser import noise_filtering

def from_point_to_pair(points: list[Point]):
    return [(p.x, p.y) for p in points]
    
class LidarCloud():
    def __init__(self, list_of_points: list[LidarPoint]):
        self._points = list_of_points
        self._lidar_tree = KDTree(from_point_to_pair(list_of_points))
        
    def __getitem__(self, index: int) -> Point:
        return self._points[index]

    def __len__(self) -> int:
        return len(self._points)

    def __iter__(self):
        return iter(self._points)

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
                self.size -= 1
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
        
def density_metric(lid_cloud: LidarCloud, rad_cloud: list[Point], size: int) -> float:
    grid_1 = Grid(lid_cloud._points, size, size)
    grid_2 = Grid(rad_cloud, size, size)
    s = 0
    keys = grid_1.data.keys() | grid_2.data.keys()
    for key in keys:
        i, j = key
        s += (grid_1.density(i, j) - grid_2.density(i, j)) ** 2
    return (s / len(keys)) ** 0.5



def find_nearest_lidar_points(lidar_cloud: LidarCloud, radar_cloud: list[Point]):
    #Находит ближайшую лидарную точку для каждой радарной точки на плоскости и расстояние до нее.
    radar_points = from_point_to_pair(radar_cloud)
    distances, indices = lidar_cloud._lidar_tree.query(radar_points) 
    return distances, [lidar_cloud._points[i] for i in indices]
    
def nearest_point_metric(lid_cloud: LidarCloud, rad_cloud: list[Point]) -> float:
    distances = find_nearest_lidar_points(lid_cloud, rad_cloud)[0]
    return ((distances ** 2).sum() / len(rad_cloud)) ** 0.5


def calc_metrics(lidar_cloud: list[LidarPoint],
                 radar_cloud: list[RadarPoint],
                 mini_delta: float = 0.06,
                 delta_t: float = 3,
                 multiply_radar_points: bool = False,
                 denoise_lidar_points: bool = False) -> tuple[float]:
    
    radar = get_fixed_radar_points(radar_cloud, mini_delta =  mini_delta)
    if denoise_lidar_points:
        lidar = noise_filtering(lidar_cloud)
    else:
        lidar = lidar_cloud
    lidar = LidarCloud(lidar_cloud)
    radar = [p for p in radar if abs(p.delta_t) < delta_t]
    if multiply_radar_points:
        radar = apply_gaussian_kernel_to_mult_radar_points(radar)
    return density_metric(lidar, radar, 300), nearest_point_metric(lidar, radar)
    

                                     
