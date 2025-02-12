class Point:
    def __init__(self, x: float, y: float, z: float, delta_t: float):
        self.x = x
        self.y = y
        self.z = z
        self.delta_t = delta_t
    def get_xyz(self):
        return self.x, self.y, self.z

class RadarPoint(Point):
    def __init__(self, point: list[int]):
        self.x = point[0]
        self.y = point[1]
        self.z = point[2]
        self.kAbsoluteRadialVelocity = point[3]
        self.kRadarCrossSection = point[4]
        self.kRelativeRadialVelocity = point[5]
        self.kRelativeLateralVelocity = point[6]
        self.kRange = point[7]
        self.kDistanceAccuracy = point[8]
        self.kAngleAccuracy = point[9]
        self.kDynProp = point[10]
        self.kHasQuality = point[11]
        self.kQPDH0 = point[12]
        self.kQDistLongRMS = point[13]
        self.kQDistLatRMS = point[14]
        self.kQVLongRMS = point[15]
        self.kQVLatRMS = point[16]
        self.kQAmbigState = point[17]
        self.kQInvalidState = point[18]
        self.delta_t = point[19]
        self.radar_idx = point[20]

class LidarPoint(Point):
    def __init__(self, point: list[int]):
        self.x = point[0]
        self.y = point[1]
        self.z = point[2]
        self.reflectance = point[3]
        self.lidar_ring = point[4]

class Data:
    def read_json(path: str) -> dict:
        import json
        with open(path) as f:
            d = json.load(f)
        return d

    def get_radars(d: dict) -> list[list[int]]:
        return d['radar']
    
    def get_lidars(d: dict) -> list[list[int]]:
        return d['lidar']

    def convert_ints_to_points(points: list[list[int]]) -> list[Point]:
        list_of_Points = []
        for point in points:
            if len(point) == 5:
                new_point = LidarPoint(point)
            elif len(point) == 21:
                new_point = RadarPoint(point)
            else:
                raise AssertionError
            list_of_Points.append(new_point)
        return list_of_Points

    def get_points_with_ratio(points: list[Point], ratio: float) -> list[Point]:
        import random
        return random.sample(points, int(len(points) * ratio))
        
    def remove_bottom_layer(points: list[LidarPoint], height) -> list[LidarPoint]:
        return [p for p in points if p.z > height]

    def remove_bad_points(points: list[RadarPoint]) -> list[RadarPoint]:
        from scipy.spatial import cKDTree
        import numpy as np
        point_coords = [[point.x, point.y] for point in points]
        tree = cKDTree(point_coords)
        distances, _ = tree.query(point_coords, k=2)
        min_distances = distances[:, 1]
        
        mean_distance = np.mean(min_distances)
        std_distance = np.std(min_distances)

        k = 1
        threshold = mean_distance + k * std_distance
        
        final_points: list[RadarPoint] = []
        
        for i, point in enumerate(points):
            if min_distances[i] <= threshold:
                final_points.append(point)
        return final_points

    def apply_gaussian_kernel_to_mult_radar_points(points: list[Point], kernel_size: int = 3, multiply_coef: float = 1.035, power: float = 1/100) -> list[Point]:
        import numpy as np
        from scipy.ndimage import gaussian_filter
        import matplotlib.pyplot as plt
        import random

        # Step 1: Define the grid
        grid_size = (3000, 3000)  # Adjust based on your surface size
        grid = np.zeros(grid_size)

        # Step 2: Place points on the grid
        for point in points:
            grid[int(point.x) * 10 + 1500, int(point.y) * 10 + 1500] += 1

        # Step 3: Apply Gaussian kernel
        sigma = kernel_size  # Adjust sigma for smoother or sharper density
        density_map = gaussian_filter(grid, sigma=sigma)

        # Step 4: Normalize (optional, depending on your use case)
        # density_map = density_map / np.sum(density_map)

        # Visualize the density map
        plt.imshow(density_map, cmap='hot', origin='lower')
        plt.colorbar(label='Density')
        plt.title('Point Density Map')
        plt.show()
        # print(np.max(density_map))
        density_map = np.power(density_map, power)
        plt.imshow(density_map, cmap='hot', origin='lower')
        plt.colorbar(label='Density')
        plt.title('Point Density Map')
        plt.show()
        counter = 0
        print(len(points))
        for i in range(3000):
            for j in range(3000):
                amount_of_points_in_sq = int(density_map[i][j] * multiply_coef)
                for k in range(amount_of_points_in_sq):
                    x = (random.random() + i - 1500) / 10
                    y = (random.random() + j - 1500) / 10
                    point = Point(x, y, 0, delta_t=0)
                    points.append(point)
                    counter += 1
              
        print(counter)
        print(len(points))
        return points