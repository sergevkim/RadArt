import json
from radart.utils.preprocessing import RadarPoint, Point

def radar_time_shift(rad_point: RadarPoint, vecs_to_rads: dict, mini_delta=0.06, unchanged=False) -> Point | RadarPoint:
    radar_idx = rad_point.radar_idx
    x0 = vecs_to_rads[str(int(radar_idx))][0]
    y0 = vecs_to_rads[str(int(radar_idx))][1]
    z0 = vecs_to_rads[str(int(radar_idx))][2]
    
    x = rad_point.initial_x - x0
    y = rad_point.initial_y - y0
    dt = mini_delta - rad_point.delta_t
    length = (x*x + y*y) ** 0.5
    v_rad = dt * rad_point.kAbsoluteRadialVelocity

    new_x = x*(v_rad + length)/length + x0
    new_y = y*(v_rad + length)/length + y0
    new_z = 0

    rad_point.x = new_x
    rad_point.y = new_y
    rad_point.z = new_z
    
    return rad_point

def get_fixed_radar_points(rad_points: list[RadarPoint], vecs_to_rads: dict, mini_delta = 0.06, unchanged = False) -> list[Point]:
    return list(map(lambda x:radar_time_shift(rad_point = x,
                                              vecs_to_rads = vecs_to_rads,
                                              mini_delta = mini_delta,
                                              unchanged=unchanged),
                    rad_points))