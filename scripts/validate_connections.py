from sys import path
from os import path as ospath, listdir
path.append(ospath.join(ospath.dirname(__file__), ".."))
import cv2
import numpy as np
import matplotlib.pyplot as plt

from util.get_asset_dirs import get_asset_dirs
from train_detection.data_readers import read_connections
from train_detection.Map import Map
from board_handling.feature_detection import find_board

convertor = {
    '2.0':0,
    '2.1':1,
    '2.2':2,
    '2.3':3,
    '3.0':4,
    '3.1':5,
    '3.2':6,
    '3.3':7,
    '4.0':8,
    '4.1':9,
    '4.2':10,
    '4.3':11,
    '5.0':12,
    '5.1':13,
    '5.2':14,
    '5.3':15,
    '6.0':16,
    '6.1':17,
    '6.2':18,
    '6.3':19
}

dir_to_run = '6.3'

def validate_connections(map):
    base_file = f"assets/0.0 Cropped/3.png"


    for asset_dir in get_asset_dirs()[convertor[dir_to_run]:]:
        files = [file for file in listdir(asset_dir) if file[-4:] == '.jpg' or file[-4:] == '.png']
        connection_data = read_connections(asset_dir)
        print(connection_data)
        for file_name in files:
            # full_file_name = ospath.join(asset_dir, file_name)
            full_file_name = f"{asset_dir}/{file_name}"


            target_file_split = full_file_name.split('/')
            main_num = target_file_split[1][:3]
            sub_num = target_file_split[2].split('.')[0]
            plt.title(f"{main_num}/{sub_num}")

            file_idx = int(file_name.split('.')[0])
            board, _ = find_board(base_file, full_file_name)
            plt.imshow(board)

            for idx in connection_data[file_idx]:
                map.connections[idx].plot(label=True)

            plt.show()
        break

if __name__ == "__main__":
    validate_connections(Map())