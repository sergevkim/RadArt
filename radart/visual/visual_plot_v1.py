from dash import Dash, dcc, html, Input, Output, callback, State
import plotly.graph_objects as go
import numpy as np

from radart.utils.preprocessing import Data, RadarPoint, LidarPoint
# import read_and_prepare_files as rpf
import plotly.graph_objects as go
import plotly
from radart.core.synchronization import get_fixed_radar_points

scene = Data.read_json('data/scenes/scene_16.json')
vec_to_rads = Data.read_json('data/radar_positions.json')

radar_ints = Data.get_radars(scene)
lidar_ints = Data.get_lidars(scene)

radar_points = Data.convert_ints_to_points(radar_ints)
lidar_points = Data.convert_ints_to_points(lidar_ints)

lidar_points = Data.get_points_with_ratio(lidar_points, 0.1)


def radar_point_to_dict(pt: RadarPoint) -> dict:
    return {
        "delta_t": pt.delta_t,
        "x": pt.x,
        "y": pt.y,
        "z": pt.z,
        # Add more fields if needed.
    }
    
radar_points_data = [radar_point_to_dict(pt) for pt in radar_points]

def road_speed(radar_point: RadarPoint) -> float:

    radar_idx = radar_point.radar_idx
    x0, y0, z0 = vec_to_rads[str(int(radar_idx))]
    x, y, z = radar_point.x, radar_point.y, radar_point.z
    speed_abs = radar_point.kAbsoluteRadialVelocity

    distance_with_radar = ((x - x0)**2 + (y - y0)**2 + (z - z0)**2)**0.5 if z is not None else ((x - x0)**2 + (y - y0)**2)**0.5

    return speed_abs * distance_with_radar

R_weighed = [abs(road_speed(pt))**0.2  for pt in radar_points]

def create_plot(radar_list: list[RadarPoint], lidar_list, DEF_SIZE=100, POINT_SIZE=1, time_shift_by=0, dt=0, figure = None):
    if figure is None:
        fig = go.Figure()
        fig.update_layout(
            scene=dict(
                xaxis=dict(range=[-DEF_SIZE, DEF_SIZE], title='X Axis'),
                yaxis=dict(range=[-DEF_SIZE, DEF_SIZE], title='Y Axis'),
                zaxis=dict(range=[-DEF_SIZE, DEF_SIZE], title='Z Axis')
            )
        )
        
        fig.update_layout(margin=dict(l=0, r=0, b=0, t=30))
    else:
        fig = go.Figure(figure)
        fig.data = []
    
    radar_list_new = radar_list
    radar_list_new = get_fixed_radar_points(radar_list_new, vec_to_rads, mini_delta=time_shift_by, unchanged=True)
    
    X_lidar = [lidar.x for lidar in lidar_list]
    Y_lidar = [lidar.y for lidar in lidar_list]
    Z_lidar = [lidar.z for lidar in lidar_list]

    fig.add_trace(go.Scatter3d(
        x=X_lidar, y=Y_lidar, z=Z_lidar,
        mode='markers',
        marker=dict(size=1, color="gray", opacity=0.8),
        name='Lidars'
    ))
    
    filtered_X = [radar.x for radar in radar_list_new if abs(radar.delta_t) < dt]
    filtered_Y = [radar.y for radar in radar_list_new if abs(radar.delta_t) < dt]
    filtered_Z = [radar.z for radar in radar_list_new if abs(radar.delta_t) < dt]
    filtered_weight = [R_weighed[i] for i in range(len(radar_list_new)) if abs(radar_list_new[i].delta_t) < dt]
    fig.add_trace(go.Scatter3d(
        x=filtered_X, y=filtered_Y, z=filtered_Z,
        mode='markers',
        marker=dict(size=2, color=filtered_weight, colorscale='jet', cmin = min(R_weighed), cmax = max(R_weighed), opacity=0.8),
        name='Primary'
    ))
    
    if figure is not None:
        figure['data'] = fig.data
        figure['layout'] = fig.layout
    return fig

# external_scripts = ['https://cdn.plot.ly/plotly-latest.min.js']
# app = Dash(__name__, external_scripts=external_scripts)
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
                step=0.01,
                value=0,
                updatemode='drag'
            ),
        ], style={'width': '45%', 'padding': '20px'}),

        html.Div([
            html.Label("Диапазон по Y:", style={'margin': '10px'}),
            dcc.Slider(
                id='y-slider',
                min=0.5,
                max=2,
                step=0.1,
                value=0.5,
                updatemode='drag'
            ),
        ], style={'width': '45%', 'padding': '20px'}),
        
        html.Div(
            id='value-display',
            style={
                'border': '2px solid #ddd',
                'padding': '20px',
                'margin-top': '20px',
                'font-size': '24px',
                'text-align': 'center',
                'width' : '17%',
            }
        )
    ], style={'display': 'flex'}),


    dcc.Graph(id='3d-plot', figure = create_plot(radar_points, lidar_points, DEF_SIZE=100, POINT_SIZE=1, time_shift_by= 0, dt = 0.5, figure=None), style={'height': '600px'}),
    dcc.Store(id='radar-store', data={
        'radar_points': radar_points_data,
        'R_weighed': R_weighed,
        'vec_to_rads': vec_to_rads
    }),
    html.Div(id='dummy-output', children = '', style={'display': 'none'})
])

@app.callback(
    Output('radar-store', 'data'),
    Input('x-slider', 'value'),
)
def update_fixed_radar(x_value):
    # Compute fixed radar points using your Python function.
    fixed_points = get_fixed_radar_points(radar_points, vec_to_rads, mini_delta=x_value, unchanged=True)
    # Convert fixed_points to JSON serializable data (e.g. a list of dicts)
    fixed_points_data = [{
        'delta_t': pt.delta_t,
        'x': pt.x,
        'y': pt.y,
        'z': pt.z
    } for pt in fixed_points]
    return {
        'fixed_radar': fixed_points_data,
        'R_weighed': R_weighed,  # if unchanged, you can store these too
        'vec_to_rads': vec_to_rads
    }


app.clientside_callback(
    '''
    function(dt, storeData) {
        if (!storeData || typeof storeData.fixed_radar === 'undefined') {
            console.error("Fixed radar data not available in store!");
            return '';
        }
        
        // Use the precomputed fixed radar data
        var radar_list = storeData.fixed_radar;
        var R_weighed = storeData.R_weighed;

        // Filter based on dt
        var newRadarX = [];
        var newRadarY = [];
        var newRadarZ = [];
        var filtered_weight = [];

        for (var i = 0; i < radar_list.length; i++) {
            if (Math.abs(radar_list[i].delta_t) < dt) {
                newRadarX.push(radar_list[i].x);
                newRadarY.push(radar_list[i].y);
                newRadarZ.push(radar_list[i].z);
                filtered_weight.push(R_weighed[i]);
            }
        }
        
        // Get the Plotly graph div and update the radar trace
        var container = document.getElementById('3d-plot');
        var graphDiv = container ? container.querySelector('.js-plotly-plot') : null;
        if (!graphDiv) {
            console.error("Graph not found!");
            return '';
        }
        if (typeof window.Plotly === 'undefined') {
            console.error("Plotly not loaded yet!");
            return '';
        }

        window.Plotly.restyle(graphDiv, {
            x: [newRadarX],
            y: [newRadarY],
            z: [newRadarZ],
            "marker.color": [filtered_weight]
        }, [1]);

        return '';
    }
    ''',
    Output('dummy-output', 'children'),
    Input('y-slider', 'value'),
    Input('radar-store', 'data')
)




if __name__ == '__main__':
    app.run_server(debug=True)
    