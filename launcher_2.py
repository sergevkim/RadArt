from argparse import ArgumentParser

from radlid_func import compare_radlid
from synchronization import get_fixed_radar_points
from read_and_prepare_files import Data, Point, RadarPoint, LidarPoint

REMOVE_BAD_POINTS = True


def main(args):
    print(args.index)
    scene = Data.read_json(args.index)

    radar_ints = Data.get_radars(scene)
    lidar_ints = Data.get_lidars(scene)

    radar_points = Data.convert_ints_to_points(radar_ints)
    lidar_points = Data.convert_ints_to_points(lidar_ints)

    lidar_points = Data.get_points_with_ratio(lidar_points, 0.1)

    radar_points = get_fixed_radar_points(radar_points)
    if REMOVE_BAD_POINTS:
        radar_points = Data.remove_bad_points(radar_points)
        
    compare_radlid(radar_list=radar_points, lidar_list=lidar_points, POINT_SIZE=1)
    
    
parser = ArgumentParser()
parser.add_argument(
    '--index', 
    type=int,
    default=16,
)
args = parser.parse_args()
main(args)