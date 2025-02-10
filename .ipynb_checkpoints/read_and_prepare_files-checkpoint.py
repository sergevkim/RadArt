class Point:
    def __init__(self, x: float, y: float, z: float, delta_t: float):
        self.x = x
        self.y = y
        self.z = z
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
    def read_json(index: int) -> dict:
        import json
        with open('data/scene_{}.json'.format(index)) as f:
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
                if not isinstance(new_point.kQPDH0, float) or new_point.kQPDH0 > 0.3:
                    continue
            else:
                raise AssertionError
            list_of_Points.append(new_point)
        return list_of_Points

    def get_points_with_ratio(points: list[Point], ratio: float) -> list[Point]:
        import random
        return random.sample(points, int(len(points) * ratio))
