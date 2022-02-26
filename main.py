import cv2
import numpy as np
import matplotlib.pyplot as plt
from board_handling.feature_detection import find_board
from train_detection.map_construction import Map

def main(target_file):
    base_file = "assets/0.0 Cropped/11.png"
    train_location_data = "assets/0.0 Cropped/trains11.csv"
    
    board = find_board(base_file, target_file)
    map = Map()
    map.plot(board)
    plt.show()

if __name__ == "__main__":
    main("assets/2.2 Red-Blue,Black,Orange/PXL_20220209_151954858.jpg")
    main("assets/2.1 Red-Yellow,Green,Gray/PXL_20220209_151741865.jpg")