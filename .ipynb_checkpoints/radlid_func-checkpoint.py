import json
import random
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import read_and_prepare_files as rpf
import plotly.graph_objects as go
import plotly
import numpy as np

def compare_radlid(radar_list: list[rpf.RadarPoint], lidar_list: list[rpf.LidarPoint], DEF_SIZE=100, POINT_SIZE=1, EPS=0):
    scenes = []
    scenes.append({})
    scenes[0]['radar'] = radar_list
    scenes[0]['lidar'] = lidar_list
    radar_coords = []
    i = 0
    temp_radar = scenes[0]['radar']
    while i < len(temp_radar):
        radar_coords.append((temp_radar[i].x, temp_radar[i].y, temp_radar[i].z, temp_radar[i].delta_t))
        i += 1
    
    X_radar = [coord[0] for coord in radar_coords]
    Y_radar = [coord[1] for coord in radar_coords]
    Z_radar = [coord[2] for coord in radar_coords]
    time = [coord[3] for coord in radar_coords]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(
        x=X_radar, y=Y_radar, z=Z_radar,
        mode='markers',
        marker=dict(size=0.3, color='red', opacity=0.8),
        name='Primary'
    ))
    
    frames = []
    
    slider_container = []
    
    for t in range(0, 21):
        t_val = t * 0.1
        filtered_X = [X_radar[i] for i in range(len(X_radar)) if abs(time[i]) < t_val]
        filtered_Y = [Y_radar[i] for i in range(len(Y_radar)) if abs(time[i]) < t_val]
        filtered_Z = [Z_radar[i] for i in range(len(Z_radar)) if abs(time[i]) < t_val]
        
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
    
    lidar_coords = []
    i = 0
    temp_lidar= np.array(scenes[0]['lidar'])
    while i < len(temp_lidar):
        if (abs(temp_lidar[i].z) > EPS):
            lidar_coords.append((temp_lidar[i].x, temp_lidar[i].y, temp_lidar[i].z, temp_lidar[i].reflectance))
        i += 1
    
    X_lidar = [coord[0] for coord in lidar_coords]
    Y_lidar = [coord[1] for coord in lidar_coords]
    Z_lidar = [coord[2] for coord in lidar_coords]
    r = [coord[3] for coord in lidar_coords]
    
    fig.add_trace(go.Scatter3d(
        x=X_lidar, y=Y_lidar, z=Z_lidar,
        mode='markers',
        marker=dict(size=POINT_SIZE, color=r, opacity=0.8),
        name='Lidars'
    ))
    
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=[
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
                    dict(
                        args=[{"visible": [True, True]}],
                        label="Show Both",
                        method="update"
                    ),
                    dict(
                        args=[{"visible": [False, False]}],  # Hide both radar and lidar
                        label="Hide Both",
                        method="update"
                    )
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
    
    lidar_frames = []
    
    plotly.offline.plot(fig, filename='test_output.html')