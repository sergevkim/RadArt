from dash import Dash, dcc, html, Input, Output, callback, State
import numpy as np

from argparse import ArgumentParser

from radart.core.lidar_denoiser import noise_filtering
from radart.metrics.metrics import LidarCloud, calc_metrics
from radart.utils.preprocessing import Data, RadarPoint, LidarPoint
import plotly.graph_objects as go
from radart.core.synchronization import get_fixed_radar_points
from radart.visual.surface import create_surface_plot


def main(args):
    scene = Data.read_json(args.scene_path)
    vec_to_rads = Data.read_json(args.radar_pos_path)

    radar_ints = Data.get_radars(scene)
    lidar_ints = Data.get_lidars(scene)

    radar_points = Data.convert_ints_to_points(radar_ints)
    lidar_points = Data.convert_ints_to_points(lidar_ints)

    lidar_points = Data.get_points_with_ratio(lidar_points, args.lidar_percentage)

    lidar_points_filtered = noise_filtering(lidar_points)

    def lidar_point_to_dict(pt: LidarPoint) -> dict:
        return {
            "x": pt.x,
            "y": pt.y,
            "z": pt.z,
        }
        
    lidar_points_data = [lidar_point_to_dict(pt) for pt in lidar_points]
    lidar_points_filtered_data = [lidar_point_to_dict(pt) for pt in lidar_points_filtered]

    lid_cloud_filtered = LidarCloud(lidar_points_filtered)

    def radar_point_to_dict(pt: RadarPoint) -> dict:
        return {
            "delta_t": pt.delta_t,
            "x": pt.x,
            "y": pt.y,
            "z": pt.z,
        }
        
    radar_points_data = [radar_point_to_dict(pt) for pt in radar_points]

    def road_speed(radar_point: RadarPoint) -> float:
        radar_idx = radar_point.radar_idx
        x0 = vec_to_rads[str(int(radar_idx))][0]
        y0 = vec_to_rads[str(int(radar_idx))][1]
        z0 = vec_to_rads[str(int(radar_idx))][2]
        x = radar_point.initial_x
        y = radar_point.initial_y
        length = ((x - x0) * (x - x0) + (y - y0) * (y - y0)) ** 0.5
        v_radar = radar_point.kAbsoluteRadialVelocity * length / (x - x0)
        return v_radar

    R_weighed = [abs(road_speed(pt))**0.2  for pt in radar_points]

    metric_graph_1, metric_graph_2 = create_surface_plot(radar_points, lidar_points_filtered, vec_to_rads)

    def create_plot(radar_list: list[RadarPoint], lidar_list, DEF_SIZE=100, POINT_SIZE=args.lidar_size, time_shift_by=0, dt=0, figure = None):
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
        html.H1("Визуализация радарных и лидарных точек", style={'textAlign': 'center'}),

        html.Div([
            html.Div([
                html.Label("Сдвиг во времени, сек:", style={'margin': '10px'}),
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
                html.Label("Временное окно, сек:", style={'margin': '10px'}),
                dcc.Slider(
                    id='y-slider',
                    min=0.5,
                    max=2,
                    step=0.1,
                    value=0.5,
                    updatemode='drag'
                ),
            ], style={'width': '45%', 'padding': '20px'}),
            
            html.Div(dcc.Checklist(
                id='lidar-noise',
                options=['Noise'],
                value=['Noise']
            )),
            
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


        dcc.Graph(id='3d-plot', figure = create_plot(radar_points, lidar_points, DEF_SIZE=100, POINT_SIZE=args.lidar_size, time_shift_by= 0, dt = 0.5, figure=None), style={'height': '600px'}),
        dcc.Graph(id='metric-surface1', figure = metric_graph_1, style={'height': '600px'}),
        dcc.Graph(id='metric-surface2', figure = metric_graph_2, style={'height': '600px'}),
        dcc.Store(id='lidar-store', data={
            'lidar_points': lidar_points_data,
            'lidar_points_filtered': lidar_points_filtered_data,
        }),
        dcc.Store(id='radar-store', data={
            'radar_points': radar_points_data,
            'R_weighed': R_weighed,
            'vec_to_rads': vec_to_rads
        }),
        html.Div(id='dummy-output1', style={'display': 'none'}),
        html.Div(id='dummy-output2', style={'display': 'none'})
    ])
    
    @app.callback(
        Output('value-display', 'children'),
        Input('x-slider', 'value'),
        Input('y-slider', 'value'),
    )
    def update_metrics_values(x_value, y_value):
        temp: tuple[float] = calc_metrics(lidar_cloud=lid_cloud_filtered, radar_cloud=radar_points, vecs_to_rads=vec_to_rads, mini_delta=x_value, delta_t=y_value)
        display_value = f"density: {temp[0]:.3f} \n nearest point: {temp[1]:.3f}"
        return display_value

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
            'radar_points': fixed_points_data,
            'R_weighed': R_weighed,  # if unchanged, you can store these too
            'vec_to_rads': vec_to_rads
        }

    app.clientside_callback(
        '''
        function(dt, storeData) {
            if (!storeData || typeof storeData.radar_points === 'undefined') {
                console.error("Fixed radar data not available in store!");
                return '';
            }
            
            // Use the precomputed fixed radar data
            var radar_list = storeData.radar_points;
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
        Output('dummy-output1', 'children'),
        Input('y-slider', 'value'),
        Input('radar-store', 'data')
    )


    app.clientside_callback(
        '''
        function(noise, storeData) {
            
            if (noise.length > 0){
                lidar_list = storeData.lidar_points;
            } else{
                lidar_list = storeData.lidar_points_filtered;
            }
            var lidarX = [];
            var lidarY = [];
            var lidarZ = [];

            for (var i = 0; i < lidar_list.length; i++) {
                lidarX.push(lidar_list[i].x);
                lidarY.push(lidar_list[i].y);
                lidarZ.push(lidar_list[i].z);
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
            
            if (noise.length > 0){
                window.Plotly.restyle(graphDiv, {
                    x: [lidarX],
                    y: [lidarY],
                    z: [lidarZ],
                    // "marker.color": 'gray',
                    "marker.size": '1',
                }, [0]);
            } else{
                window.Plotly.restyle(graphDiv, {
                    x: [lidarX],
                    y: [lidarY],
                    z: [lidarZ],
                    // "marker.color": 'red',
                    "marker.size": '2',
                }, [0]);
            }


            return '';
        }
        ''',
        Output('dummy-output2', 'children'),
        Input('lidar-noise', 'value'),
        State('lidar-store', 'data')
    )
    #if __name__ == '__main__':
    app.run_server(debug=False)