from sys import path
from os import path as ospath, listdir

path.append(ospath.join(ospath.dirname(__file__), ".."))
import cv2
import numpy as np
import matplotlib.pyplot as plt

from datasets.cities import cities_loader

city_loader = cities_loader()
city_list = city_loader.get_cities_list()
counter = 0
out_string = ""

def onclick(event):
    global counter, out_string
    city = city_list[counter]
    print(current_string := f"{city},{event.xdata},{event.ydata}\n")
    out_string += current_string
    counter += 1
    print(city_list[counter])
    

def show_city_clickable(avg_img):
    # avg_img = cv2.cvtColor(avg_img, 4)
    fig = plt.figure(1)
    ax = fig.add_subplot(111)
    ax.imshow(avg_img)
    fig.canvas.mpl_connect('key_press_event', onclick)
    print(city_list[0])
    plt.show()
    print(out_string)
    return out_string

if __name__ == "__main__":
    avg_img_file = "assets/0.0 Cropped/11.png"
    avg_img = cv2.imread(avg_img_file, 1)
    show_city_clickable(avg_img)