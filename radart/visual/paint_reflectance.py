import json
import random
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import radart.utils.preprocessing as rpf
import plotly.graph_objects as go
import plotly
import numpy as np

def paint_r(radar_list: list[rpf.RadarPoint], lidar_list: list[rpf.LidarPoint], DEF_SIZE=100, POINT_SIZE=1, EPS=0):
    X_radar = [radar.x for radar in radar_list]
    Y_radar = [radar.y for radar in radar_list]
    Z_radar = [radar.z for radar in radar_list]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(
        x=[], y=[], z=[],
        mode='markers',
        marker=dict(size=POINT_SIZE, color='red', opacity=0.8),
        name='Primary'
    ))
    
    frames = []
    
    slider_container = []
    
    for t in range(1, 21):
        t_val = t * 0.1
        filtered_X = [radar.x for radar in radar_list if abs(radar.delta_t) < t_val]
        filtered_Y = [radar.y for radar in radar_list if abs(radar.delta_t) < t_val]
        filtered_Z = [radar.z for radar in radar_list if abs(radar.delta_t) < t_val]
        
        frame = go.Frame(
            data=[go.Scatter3d(
                x=filtered_X, y=filtered_Y, z=filtered_Z,
                mode='markers',
                marker=dict(size=POINT_SIZE, color='red', opacity=0.8),
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
            'label': f'{t_val:.1f} s',
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
    
    plotly.offline.plot(fig, filename='test_output.html')