from dash import Dash, dcc, html, Input, Output, callback, State
import plotly.graph_objects as go
import numpy as np
from copy import deepcopy

from argparse import ArgumentParser

from radart.utils.preprocessing import Data, RadarPoint, LidarPoint
# import read_and_prepare_files as rpf
import plotly.graph_objects as go
import plotly
from radart.core.synchronization import get_fixed_radar_points
from radart.metrics.metrics import calc_metrics, LidarCloud
from radart.core.lidar_denoiser import noise_filtering
import radart.visual.visual_plot_v1 as rvp


def main(args):
  rvp.main(args)
        
parser = ArgumentParser()
parser.add_argument(
  '--scene_path', 
  type=str,
  default='data/scenes/scene_16.json',
)

parser.add_argument(
  '--radar_pos_path', 
  type=str,
  default='data/radar_positions.json',
)

parser.add_argument(
  '--lidar_percentage', 
  type=float,
  default=0.1,
)

parser.add_argument(
  '--radar_size', 
  type=float,
  default=2,
)

parser.add_argument(
  '--lidar_size', 
  type=float,
  default=1,
)

args = parser.parse_args()
main(args)