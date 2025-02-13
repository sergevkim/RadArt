import radart.visual.visual_plot_v1 as rvp

from argparse import ArgumentParser


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