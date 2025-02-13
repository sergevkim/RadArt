import argparse
import json
from radart.metrics.metrics import  LidarCloud, calc_metrics
from radart.utils.preprocessing import  Data

def main():
    parser = argparse.ArgumentParser(description="Обрабатывает параметры запуска")

    parser.add_argument("--scene_path",
                        type = str,
                        default = "data/scenes/scene_1.json",
                        help = "Путь до сцены")
    
    parser.add_argument("--radar_positions_path",
                       type = str,
                       default = "radar_positions.json",
                       help = "Путь до координат радаров")
    
    parser.add_argument("--mini_delta",
                        type=float,
                        default=0.06,
                        help="Смещение времени")
    
    parser.add_argument("--delta_t",
                        type=float,
                        default=3,
                        help="Временное окно")
    
    parser.add_argument("--nearest_point",
                        action="store_true",
                        help="Использовать метрику ближайшего соседа")
    
    parser.add_argument("--denoise_lidar",
                        action="store_true",
                        help="Очистка лидарных точек от больших плоских поверхностей (в частности, дороги)")
    
    parser.add_argument("--multiply_radar_points",
                        action="store_true",
                        help="Разгладить и размножить радарные точки")
    
    parser.add_argument("--density",
                        action="store_true",
                        help="Использовать density-метрику")
    
    args = parser.parse_args()
    
    scene_path = args.scene_path
    vecs_to_rads_path = args.radar_positions_path
    mini_delta = args.mini_delta
    delta_t = args.delta_t
    density = args.density
    nearest_point = args.nearest_point
    denoise_lidar = args.denoise_lidar
    multiply_radar_points = args.multiply_radar_points
    
    
    #Прочтение данных
    data = Data.read_json(scene_path)
    lidar = LidarCloud(Data.convert_ints_to_points(data['lidar']))
    radar = Data.convert_ints_to_points(data['radar'])
    
    with open(vecs_to_rads_path) as f:
        vecs_to_rads = json.load(f)
        
    
    results = calc_metrics(lidar_cloud = lidar,
                           radar_cloud = radar,
                           vecs_to_rads = vecs_to_rads,
                           mini_delta = mini_delta,
                           delta_t = delta_t,
                           multiply_radar_points = multiply_radar_points,
                           denoise_lidar_points = denoise_lidar)
    
    
    # Выводим полученные значения
    if density:
        print("Density metric:", results[0])
    if nearest_point:
        print("Nearest point metric:", results[1])
    if not density and not nearest_point:
        print("Densiti metric:", results[0])
        print("Nearest point metric:", results[1])


if __name__ == "__main__":
    main()
