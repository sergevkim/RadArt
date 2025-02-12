from dash import Dash, dcc, html, Input, Output, callback
import plotly.graph_objects as go
import numpy as np

from radart.utils.preprocessing import Data, RadarPoint, LidarPoint
import json
# import read_and_prepare_files as rpf
import plotly.graph_objects as go
import plotly
from radart.core.synchronization import get_fixed_radar_points

scene = Data.read_json(16)

radar_ints = Data.get_radars(scene)
lidar_ints = Data.get_lidars(scene)

radar_points = Data.convert_ints_to_points(radar_ints)
lidar_points = Data.convert_ints_to_points(lidar_ints)

lidar_points = Data.get_points_with_ratio(lidar_points, 0.1)

def create_plot(radar_list: list[RadarPoint], DEF_SIZE=100, POINT_SIZE=1, time_shift_by=0, dt=0):
    fig = go.Figure()
    
    radar_list_new = radar_list
    radar_list_new = get_fixed_radar_points(radar_list_new, mini_delta=time_shift_by, unchanged=True)
    
    
    filtered_X = [radar.x for radar in radar_list_new if abs(radar.delta_t) < dt]
    filtered_Y = [radar.y for radar in radar_list_new if abs(radar.delta_t) < dt]
    filtered_Z = [radar.z for radar in radar_list_new if abs(radar.delta_t) < dt]
    
    fig.add_trace(go.Scatter3d(
        x=np.array(filtered_X), y=np.array(filtered_Y), z=np.array(filtered_Z),
        mode='markers',
        marker=dict(size=POINT_SIZE, color='red', opacity=0.8),
        name='Primary'
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
    html.H1("3D График функции двух переменных", style={'textAlign': 'center'}),

    html.Div([
        html.Div([
            html.Label("Диапазон по X:", style={'margin': '10px'}),
            dcc.Slider(
                id='x-slider',
                min=-0.1,
                max= 0.1,
                step=0.05,
                value=0,
                marks={i * 0.05: str(i * 0.05) for i in range(-2, 3)},
                updatemode='drag'
            ),
        ], style={'width': '45%', 'padding': '20px'}),

        html.Div([
            html.Label("Диапазон по Y:", style={'margin': '10px'}),
            dcc.Slider(
                id='y-slider',
                min=0.5,
                max=2,
                step=0.5,
                value=0.5,
                marks={i * 0.5 : str(i * 0.5) for i in range(1, 5)},
                updatemode='drag'
            ),
        ], style={'width': '45%', 'padding': '20px'})
    ], style={'display': 'flex'}),


    dcc.Graph(id='3d-plot', style={'height': '600px'})
])


@callback(
    Output('3d-plot', 'figure'),
    Input('x-slider', 'value'),
    Input('y-slider', 'value')
)

def update_plot(x_value, y_value):
    return create_plot(radar_points, DEF_SIZE=100, POINT_SIZE=1, time_shift_by= x_value, dt = y_value)


if __name__ == '__main__':
    app.run_server(debug=True)
