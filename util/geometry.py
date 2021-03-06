from sys import path
from os import path as ospath
path.append(ospath.join(ospath.dirname(__file__), ".."))

import matplotlib.pyplot as plt
import cv2
from shapely.geometry import Polygon, Point as ShapelyPoint
import numpy as np

class Quadrilateral():
    def __init__(self, p1, p2, p3, p4):
        self.points = np.array([p1, p2, p3, p4], dtype=Point)
        
        self._xs = np.array([p.x for p in self.points], dtype=np.float32)
        self._ys = np.array([p.y for p in self.points], dtype=np.float32)
        
        self.max_x = self._xs.max(0)
        self.min_x = self._xs.min(0)

        self.max_y = self._ys.max(0)
        self.min_y = self._ys.min(0)

    def plot(self, image=None, show=False, colour=None, fill=False):
        if colour is not None:
            colour = np.array(colour/255, np.float32)
        if image is not None:
            plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if fill:
            plt.fill(self._xs, self._ys, color=colour)
        else:
            for boundary in self.getEdgeLines():
                boundary.plot(show=False, colour=colour)
        if show:
            plt.show()

    # Method returns shape as shapely.geometry.Polygon object to make use of the shape.geometry.Point.within() function that is able to quickly tell if a point is within a polygon
    def as_shapely_polygon(self):
        return Polygon([(p.x, p.y) for p in self.points])

    def getEdgeLines(self):
        boundaries = []
        for i in range(-1, len(self.points)-1):
            boundaries.append(Segment(*self.points[i], *self.points[i+1]))
        return boundaries

class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def within(self, polygon):
        shapely_polygon = polygon.as_shapely_polygon()
        return self.as_shapely_point().within(shapely_polygon)

    # Method returns shape as shapely.geometry.Point object to make use of the shape.geometry.Point.within() function that is able to quickly tell if a point is within a polygon
    def as_shapely_point(self):
        return ShapelyPoint(self.x, self.y)

    def plot(self, image=None, show=False):
        if image is not None:
            plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        plt.scatter(self.x, self.y)
    
    def __str__(self):
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return self.__str__()
    
    def __iter__(self):
        return iter([self.x, self.y])
    
    def isValid(self):
        return self.x is not None and self.y is not None

class Line():
    def __init__(self, grad, intercept=None, x_intercept=None, min_x=-np.inf, min_y = -np.inf, max_x = np.inf, max_y = np.inf):
        self.grad = grad
        self.y_intercept = intercept
        self.x_intercept = x_intercept
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y
            
    def get_y(self, x):
        if isBetween(self.min_x, self.max_x, x):
            if self.is_vertical():
                return None
            elif self.is_horizontal():
                return self.y_intercept
            else:
                return self.grad*x + self.y_intercept
        
    def get_x(self, y):
        if isBetween(self.min_y, self.max_y, y):
            if self.is_vertical():
                return self.x_intercept
            elif self.is_horizontal():
                return None
            else:
                return (y - self.y_intercept)/self.grad
    
    def __repr__(self):
        return f"(Grad: {self.grad}, y_intercept: {self.y_intercept}, x_intercept: {self.x_intercept})"

    def plot(self, image=None, show=True):
        if image is not None:
            plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            (max_y, max_x, _) = image.shape
        else:
            max_y, max_x = 10000, 10000
        min_x, min_y = -max_x, -max_y
        
        line_points = []
        
        if self.is_horizontal():
            line_points = [(min_x, max_x), (self.get_y(min_x), self.get_y(max_x))]
        elif self.is_vertical():
            line_points = [(self.get_x(min_y), self.get_x(max_y)), (min_y, max_y)]
        else:
            line_points = [(self.get_x(min_y), self.get_x(min_y)), (self.get_y(min_x), self.get_y(max_x))]
        
        plt.plot(*line_points)
        
        if show:
            plt.show()
        

    def plot_cv(self, image, colour):
        (max_y, max_x, _) = image.shape
        min_x, min_y = 0, 0
        
        if self.is_horizontal():
            pt0 = (min_x, self.y_intercept)
            pt1 = (max_x, self.y_intercept)
        elif self.is_vertical():
            pt0 = (self.x_intercept, min_y)
            pt1 = (self.x_intercept, max_y)
        else:
            pt0 = (min_x, self.get_y(min_x))
            pt1 = (max_x, self.get_y(max_x))
            
        pt0 = (int(pt0[0]), int(pt0[1]))
        pt1 = (int(pt1[0]), int(pt1[1]))
            
        cv2.line(image, pt0, pt1, colour, 3)
        # print(f"Line Plotted: ({pt0}) -> ({pt1}) (Grad: {self.grad}, y_intercept: {self.y_intercept}, x_intercept: {self.x_intercept}, colour: {colour})")
        return image
    
    
    def is_vertical(self):
        return np.isinf(self.grad)
    
    
    def is_horizontal(self):
        return self.grad == 0
    
    
    def find_intersection(self, other_line):
    
        if self.is_vertical() and other_line.is_vertical(): # both are vertical
            return NonePoint()
        if self.is_horizontal() and other_line.is_horizontal():
            return NonePoint()
        
        if self.is_vertical():
            return Point(self.x_intercept, other_line.get_y(self.x_intercept))
        elif other_line.is_vertical():
            return Point(other_line.x_intercept, self.get_y(other_line.x_intercept))
        elif self.is_horizontal():
            return Point(other_line.get_x(self.y_intercept), self.y_intercept)
        elif other_line.is_horizontal():
            return Point(self.get_x(other_line.y_intercept), other_line.y_intercept)
        else:
            shared_x = (other_line.y_intercept - self.y_intercept)/(self.grad - other_line.grad)
            shared_y = self.get_y(shared_x)
            return Point(shared_x, shared_y)

    def construct_line_from_points(x0, y0, x1, y1):
        if x0 == x1:
            return Line(np.inf, x_intercept=x0)
        if y0 == y1:
            return Line(0, intercept=y0)
        grad = (y1-y0)/(x1-x0)
        intercept = y0 - grad*x0
        
        min_x = np.min([x0, x1])
        max_x = np.max([x0, x1])
        
        min_y = np.min([y0, y1])
        max_y = np.max([y0, y1])
        
        return Line(grad, intercept, min_x=min_x, min_y=min_y, max_x=max_x, max_y=max_y)

class Segment(Line):
    def __init__(self, x0, y0, x1, y1):
        self.grad = None
        self.x_intercept = None
        self.y_intercept = None
        self.p1 = Point(x0, y0)
        self.p2 = Point(x1, y1)
        
        self.min_x = np.array([x0, x1], dtype=np.float32).min(0)
        self.max_x = np.array([x0, x1], dtype=np.float32).max(0)
        
        self.min_y = np.array([y0, y1], dtype=np.float32).min(0)
        self.max_y = np.array([y0, y1], dtype=np.float32).max(0)
        
        if x0 == x1:
            self.grad = np.inf 
            self.x_intercept = x0
        elif y0 == y1:
            self.grad = 0 
            self.y_intercept = y0
        else:
            self.grad = (y1-y0)/(x1-x0)
            self.y_intercept = y0 - self.grad*x0
            self.x_intercept = -self.y_intercept/self.grad
            
    def find_intersection(self, other_line):
        intersectionPoint =  super().find_intersection(other_line)
        if isBetween(self.max_x, self.min_x, intersectionPoint.x) and isBetween(self.max_y, self.min_y, intersectionPoint.y):
            return intersectionPoint
        else:
            return NonePoint()
        
    def plot(self, image=None, show=True, colour=None):
            
        line_points = [(self.p1.x, self.p2.x), (self.p1.y, self.p2.y)]
        
        if image is not None:
            plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        if colour is not None:
            plt.plot(*line_points, color=colour)
        else:
            plt.plot(*line_points)
        
        if show:
            plt.show()

class NonePoint(Point):
    def __init__(self):
        super().__init__(0, 0)
        
    def isValid(self):
        return False

# Returns true if z is between x and y
def isBetween(x,y,z):
    a = np.max([x,y])
    b = np.min([x,y])
    # print(f"{a >= z >= b}:{a} >= {z} >= {b}")
    return a >= z >= b


if __name__ == "__main__":
    p4 = Point(1,4)
    p1 = Point(2,2)
    p2 = Point(4,2)
    p3 = Point(3,4)

    p5 = Point(1.08, 3.97)

    q = Quadrilateral(p1, p2, p3, p4)
    print(p5.within(q))