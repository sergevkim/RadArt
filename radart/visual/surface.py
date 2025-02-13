import numpy as np
import plotly.graph_objects as go
from radart.utils.preprocessing import Data, RadarPoint, LidarPoint
from radart.metrics.metrics import calc_metrics, LidarCloud


def create_surface_plot(radar_points, lidar_points, vec_to_rads):
    delta_t_values = np.arange(0.5, 2.1, 0.1)
    mini_delta_values = np.arange(-0.1, 0.1, 0.01)
    X, Y = np.meshgrid(delta_t_values, mini_delta_values)
    Z_density = np.zeros(X.shape)
    Z_nearest = np.zeros(X.shape)

    for i, mini_delta in enumerate(mini_delta_values):
        for j, delta_t in enumerate(delta_t_values):

            sampled_radar = radar_points
            sampled_lidar = Data.get_points_with_ratio(lidar_points, 0.1)

            if not sampled_radar and not sampled_lidar:
                Z_density[i, j] = 0
                Z_nearest[i, j] = 0
                continue

            # for p in sampled_radar:
            #     if isinstance(p, RadarPoint):
            #         p.delta_t = delta_t

            combined = sampled_radar + sampled_lidar

            if not combined:
                Z_density[i, j] = 0
                Z_nearest[i, j] = 0
                continue

            try:
                filtered = Data.remove_bad_points(combined)
            except ValueError:
                Z_density[i, j] = 0
                Z_nearest[i, j] = 0
                continue
            

            radar_cloud = [p for p in filtered if isinstance(p, RadarPoint)]
            lidar_cloud = LidarCloud([p for p in filtered if isinstance(p, LidarPoint)])

            if not radar_cloud or not lidar_cloud:
                Z_density[i, j] = 0
                Z_nearest[i, j] = 0
                continue

            density_metric, nearest_metric = calc_metrics(
                lidar_cloud=lidar_cloud,
                radar_cloud=radar_cloud,
                vecs_to_rads=vec_to_rads,
                mini_delta=mini_delta,
                delta_t=delta_t,
                multiply_radar_points=False,
                denoise_lidar_points=False
            )

            Z_density[i, j] = density_metric
            Z_nearest[i, j] = nearest_metric

    fig_density = go.Figure()
    fig_nearest = go.Figure()

    if np.any(Z_density):
        fig_density.add_trace(go.Surface(
            x=X, y=Y, z=Z_density,
            colorscale='Viridis',
            name='Density Metric',
            opacity=0.7
        ))

    if np.any(Z_nearest):
        fig_nearest.add_trace(go.Surface(
            x=X, y=Y, z=Z_nearest,
            colorscale='Plasma',
            name='Nearest Point Metric',
            opacity=0.7
        ))

    for fig, title in zip([fig_density, fig_nearest], ['Density metric', 'Nearest metric']):
        fig.update_layout(
            title={
                'text' : title,
                'x':0.5,
                'xanchor': 'center'
            },
            scene=dict(
                xaxis_title='delta_t',
                yaxis_title='mini_delta',
                zaxis_title='Metric Value',
                camera_eye=dict(x=1.5, y=1.5, z=0.8)
            ),
            width=1200,
            height=600,
            margin=dict(l=60, r=60, b=60, t=60)
        )

    return fig_density, fig_nearest