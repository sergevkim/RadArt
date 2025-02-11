import json
import random
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import read_and_prepare_files as rpf
import plotly.graph_objects as go
import plotly
import numpy as np

def road_speed(radar_point: rpf.RadarPoint) -> float:
    with open('radar_positions.json') as f:
        vecs_to_rads = json.load(f)
    radar_idx = radar_point.radar_idx
    x0, y0, z0 = vecs_to_rads[str(int(radar_idx))]
    x, y, z = radar_point.x, radar_point.y, radar_point.z
    speed_abs = radar_point.kAbsoluteRadialVelocity

    # Use proper 3D distance for calculations, including z if needed
    distance_with_radar = ((x - x0)**2 + (y - y0)**2 + (z - z0)**2)**0.5 if z is not None else ((x - x0)**2 + (y - y0)**2)**0.5

    # Ensure vector direction and radial velocity influenced determination
    return speed_abs * distance_with_radar

def radar_time_shift_unchange(rad_point: rpf.RadarPoint, mini_delta = 0.06) -> rpf.Point:
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
    new_z = 0
    point_new = rpf.Point(new_x, new_y, new_z, rad_point.delta_t)
    
    return point_new 

def get_fixed_radar_points_unchange(rad_points: list[rpf.RadarPoint], mini_delta1 = 0.06) -> list[rpf.Point]:
    return list(map(lambda x:radar_time_shift_unchange(x, mini_delta = mini_delta1), rad_points))

def delay_variety(radar_list: list[rpf.RadarPoint], lidar_list: list[rpf.LidarPoint], DEF_SIZE=100, POINT_SIZE=1, EPS=0):
    
    X_radar = [radar.x for radar in radar_list]
    Y_radar = [radar.y for radar in radar_list]
    Z_radar = [radar.z for radar in radar_list]

    R_weighed = [abs(road_speed(pt))**0.2  for pt in radar_list]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(
        x=[], y=[], z=[],
        mode='markers',
        marker=dict(size=POINT_SIZE, color='red', opacity=0.8),
        name='Primary'
    ))
    
    frames = []
    
    slider_container = []
    
    for t in range(-50, 51):
        t_val = t * 0.005
        
        radar_list_new = radar_list
        radar_list_new = get_fixed_radar_points_unchange(radar_list_new, mini_delta1=t_val)
        
        filtered_X = [radar.x for radar in radar_list_new]
        filtered_Y = [radar.y for radar in radar_list_new]
        filtered_Z = [radar.z for radar in radar_list_new]
        
        frame = go.Frame(
            data=[go.Scatter3d(
                x=filtered_X, y=filtered_Y, z=filtered_Z,
                mode='markers',
                marker=dict(size=POINT_SIZE, color=R_weighed, colorscale='Jet', opacity=0.8, colorbar=dict(title='Color Scale')),
                name='Radars'
            )],
            name=str(t_val)
        )
        frames.append(frame)
    
        slider_step = {
            'args': [
                [frame.name],
                {'frame': {'duration': 300, 'redraw': True}, 'mode': 'immediate', 'transition': {'duration': 300}}
            ],
            'label': f'{t_val} s',
            'method': 'animate'
        }
        slider_container.append(slider_step)
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[-DEF_SIZE, DEF_SIZE], title='X Axis'),
            yaxis=dict(range=[-DEF_SIZE, DEF_SIZE], title='Y Axis'),
            zaxis=dict(range=[-DEF_SIZE, DEF_SIZE], title='Z Axis')
        ),
        sliders=[
            {
                'active': 0,
                'yanchor': 'top',
                'xanchor': 'left',
                'currentvalue': {
                    'font': {'size': 20},
                    'prefix': 'Time: ',
                    'visible': True,
                    'xanchor': 'right'
                },
                'transition': {'duration': 300, 'easing': 'cubic-in-out'},
                'pad': {'b': 10, 't': 50},
                'len': 0.9,
                'x': 0.1,
                'y': 0,
                'steps': slider_container
            }
        ]
    )
    
    fig.frames = frames
    
    X_lidar = [lidar.x for lidar in lidar_list]
    Y_lidar = [lidar.y for lidar in lidar_list]
    Z_lidar = [lidar.z for lidar in lidar_list]
    R_lidar = [lidar.reflectance for lidar in lidar_list]

    R_weighed = [ref**0.35 for ref in R_lidar]    
    
    fig.add_trace(go.Scatter3d(
        x=X_lidar, y=Y_lidar, z=Z_lidar,
        mode='markers',
        marker=dict(size=POINT_SIZE, color=R_weighed, colorscale='Jet', opacity=0.8, colorbar=dict(title='Color Scale')),
        name='Lidars'
    ))
    
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=[
                    dict(
                        args=[{"visible": [True, True]}],
                        label="Show Both",
                        method="update"
                    ),
                    dict(
                        args=[{"visible": [True, False]}],
                        label="Show Radar",
                        method="update"
                    ),
                    dict(
                        args=[{"visible": [False, True]}],
                        label="Show Lidar",
                        method="update"
                    ),
                ],
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.1,
                xanchor="left",
                y=1.1,
                yanchor="top"
            ),
        ]
    )
    
    plotly.offline.plot(fig, filename='test_output_variety.html')