from dash import Dash, dcc, html, Input, Output, callback
import plotly.graph_objects as go
import numpy as np

from synchronization import get_fixed_radar_points
from read_and_prepare_files import Data
import json
import read_and_prepare_files as rpf
import plotly.graph_objects as go
import plotly
from synchronization import get_fixed_radar_points

def road_speed(radar_point: rpf.RadarPoint) -> float:
    with open('radar_positions.json') as f:
        vecs_to_rads = json.load(f)
    radar_idx = radar_point.radar_idx
    x0, y0, z0 = vecs_to_rads[str(int(radar_idx))]
    x, y, z = radar_point.x, radar_point.y, radar_point.z
    speed_abs = radar_point.kAbsoluteRadialVelocity

    distance_with_radar = ((x - x0)**2 + (y - y0)**2 + (z - z0)**2)**0.5 if z is not None else ((x - x0)**2 + (y - y0)**2)**0.5

    return speed_abs * distance_with_radar

scene = Data.read_json(16)

radar_ints = Data.get_radars(scene)
lidar_ints = Data.get_lidars(scene)

radar_points = Data.convert_ints_to_points(radar_ints)
lidar_points = Data.convert_ints_to_points(lidar_ints)

lidar_points = Data.get_points_with_ratio(lidar_points, 0.1)

R_weighed = [abs(road_speed(pt))**0.2  for pt in radar_points]

def create_plot(radar_list: list[rpf.RadarPoint], lidar_list: list[rpf.LidarPoint], DEF_SIZE=100, POINT_SIZE=1, time_shift_by=0, dt=0):
    fig = go.Figure()

    radar_list_new = radar_list
    radar_list_new = get_fixed_radar_points(radar_list_new, mini_delta=time_shift_by, unchanged=True)

    filtered_X = [radar.x for radar in radar_list_new if abs(radar.delta_t) < dt]
    filtered_Y = [radar.y for radar in radar_list_new if abs(radar.delta_t) < dt]
    filtered_Z = [radar.z for radar in radar_list_new if abs(radar.delta_t) < dt]

    filtered_weight = [R_weighed[i] for i in range(len(radar_list_new)) if abs(radar_list_new[i].delta_t) < dt]

    fig.add_trace(go.Scatter3d(
        x=np.array(filtered_X), y=np.array(filtered_Y), z=np.array(filtered_Z),
        mode='markers',
        marker=dict(size=POINT_SIZE, color=filtered_weight, colorscale='Jet', opacity=0.8),
        name='Radars'
    ))
    
    X_lidar = [lidar.x for lidar in lidar_list]
    Y_lidar = [lidar.y for lidar in lidar_list]
    Z_lidar = [lidar.z for lidar in lidar_list]
    
    fig.add_trace(go.Scatter3d(
        x=X_lidar, y=Y_lidar, z=Z_lidar,
        mode='markers',
        marker=dict(size=POINT_SIZE, color= "gray", opacity=0.8),
        name='Lidars'
    ))
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[-DEF_SIZE, DEF_SIZE], title='X Axis'),
            yaxis=dict(range=[-DEF_SIZE, DEF_SIZE], title='Y Axis'),
            zaxis=dict(range=[-DEF_SIZE, DEF_SIZE], title='Z Axis')
        )
    )
    
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=30))
    return fig


app = Dash(__name__)
server = app.server


app.layout = html.Div([
    html.H1("Радарные и лидарные точки", style={'textAlign': 'center'}),

    html.Div([
        html.Div([
            html.Label("Сдвиг по времени:", style={'margin': '10px'}),
            dcc.Slider(
                id='x-slider',
                min=-0.1,
                max= 0.1,
                step=0.01,
                value=0,
                marks={i * 0.01: str(i * 0.01) for i in range(-10, 11)},
                updatemode='drag'
            ),
        ], style={'width': '45%', 'padding': '20px'}),

        html.Div([
            html.Label("Размер временного промежутка:", style={'margin': '10px'}),
            dcc.Slider(
                id='y-slider',
                min=0.5,
                max=2,
                step=0.1,
                value=0.5,
                marks={i / 5.0: str(i / 5.0) for i in range(1, 11)},
                updatemode='drag'
            ),
        ], style={'width': '45%', 'padding': '20px'}),
        # Плашка с вещественным значением
        html.Div(
            id='value-display',
            style={
                'border': '2px solid #ddd',
                'padding': '20px',
                'margin-top': '20px',
                'font-size': '24px',
                'text-align': 'center'
            }
        )
    ], style={'display': 'flex'}),

    # Область с графиком
    dcc.Graph(id='3d-plot', style={'height': '600px'})
])


# Колбэк для обновления графика
@callback(
    Output('3d-plot', 'figure'),
    Output('value-display', 'children'),
    Input('x-slider', 'value'),
    Input('y-slider', 'value')
)

def update_plot_and_display(x_value, y_value):
    display_value = f"Текущее значение: {x_value:.3f}"

    return create_plot(radar_points, lidar_points,  DEF_SIZE=100, POINT_SIZE=1, time_shift_by= x_value, dt = y_value), display_value


if __name__ == '__main__':
    app.run_server(debug=True)