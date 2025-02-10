import json
from read_and_prepare_files import RadarPoint, Point

def radar_time_shift(rad_point: RadarPoint, mini_delta = 0.06) -> Point:
    with open('radar_positions.json') as f:
        vecs_to_rads = json.load(f)
    radar_idx = rad_point.radar_idx
    x0 = vecs_to_rads[str(int(radar_idx))][0]
    y0 = vecs_to_rads[str(int(radar_idx))][1]
    z0 = vecs_to_rads[str(int(radar_idx))][2]
    
    x = rad_point.x - x0
    y = rad_point.y - y0
    dt = mini_delta - rad_point.delta_t
    length = (x*x + y*y) ** 0.5
    v_rad = dt * rad_point.kAbsoluteRadialVelocity

    new_x = x*(v_rad + length)/length + x0
    new_y = y*(v_rad + length)/length + y0
    new_z = z0

    rad_point.x = new_x
    rad_point.y = new_y
    rad_point.z = new_z
    
    return rad_point

def get_fixed_radar_points(rad_points: list[RadarPoint]) -> list[Point]:
    return list(map(radar_time_shift, rad_points))