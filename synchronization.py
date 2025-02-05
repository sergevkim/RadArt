import json
from read_and_prepare_files import RadarPoint, Point

def radar_time_shift(rad_point: RadarPoint) -> Point:
    with open('radar_positions.json') as f:
        vecs_to_rads = json.load(f)
    radar_idx = rad_point.radar_idx
    x0 = vecs_to_rads[str(int(radar_idx))][0]
    y0 = vecs_to_rads[str(int(radar_idx))][1]
    z0 = vecs_to_rads[str(int(radar_idx))][2]
    
    x = rad_point.x - x0
    y = rad_point.y - y0
    dt = rad_point.delta_t
    lenght = (x*x + y*y) ** 0.5
    v_rad = rad_point.kRelativeRadialVelocity
    v_lat = rad_point.kRelativeLateralVelocity
    
    
    return Point(x + (x*v_rad/lenght + y*v_lat/lenght) * dt + x0, y + (y*v_rad/lenght - x*v_lat/lenght) * dt + y0, z0)

def get_fixed_radar_points(rad_points: list[RadarPoint]) -> list[Point]:
    return list(map(radar_time_shift, rad_points))