from sys import path
from os import path as ospath

path.append(ospath.join(ospath.dirname(__file__), ".."))

import numpy as np
import matplotlib.pyplot as plt
from concurrent import futures

from train_detection.Connection import Connection
from train_detection.BoardSegment import BoardSegment
from train_detection.data_readers import read_base_colours_file, read_layout_csv, read_segment_file
from datasets.dataset import index_to_dir
from board_handling.feature_detection import find_board
from util.constants import BASE_BACKGROUND_COLOUR
from util.timer import timer

class Map():
    def __init__(self, layout_info='assets/0.0 Cropped/trains11.csv', segment_info = 'assets/segment_info.csv', layout_colours='assets/0.0 Cropped/avg_colours11.csv'):

        self.connections: list(Connection) = []

        train_layouts = read_layout_csv(layout_info)
        base_colours = read_base_colours_file(layout_colours)

        for i, connection_info in enumerate(read_segment_file(segment_info)):
            city1 = connection_info[0][0]
            city2 = connection_info[0][1]
            connection_colour = train_layouts[connection_info[1][0]-1][0]
            segments = []
            for segment_index in connection_info[1]:
                coordinates = train_layouts[segment_index-1][1]
                # base_colour = base_colours[segment_index-1]
                base_colour = connection_colour
                segments.append(BoardSegment(base_colour, *coordinates, segment_index))
            
            self.connections.append(Connection(city1, city2, segments, connection_colour, i))

    def plot(self, image=None, show=False, label=False):
        if image is not None:
            plt.imshow(image)

        connection: Connection
        for connection in self.connections:
            connection.plot(image=None, show=False, label=label)
        

        if show:
            plt.show()    
    
    @timer
    def process_multicore_results(self, board):
        results = []
        with futures.ProcessPoolExecutor() as executor:
            # 
            # Runs connection.hasTrainResults(board) multi-threaded. 
            # 
            # Map.processes_singlecore(self, board)  function performs the same task but sequentially and is slightly easier
            #   to understand 
            # 
            processes = [executor.submit(connection.hasTrainResults, board) for connection in self.connections]
            for process in processes:
                results.append(process.result())
        return results

    def process_multicore(self, board):
        results = []
        with futures.ProcessPoolExecutor() as executor:
            processes = [executor.submit(connection.hasTrain, board) for connection in self.connections]
            for process in processes:
                results.append(process.result())
        return results

    @timer
    def process_singlecore(self, board):
        results = []
        for connection in self.connections:
            results.append(connection.hasTrain(board))
        return results
    
if __name__ == "__main__":
    sample_image, _ = find_board("assets/0.0 Cropped/3.png", index_to_dir(1,0,1))
    empty_image = np.full((2000,3000, 3), BASE_BACKGROUND_COLOUR)
    map = Map()
    
    map.plot(show=True, image=sample_image)