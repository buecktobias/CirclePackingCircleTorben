import secrets
from math import sqrt
import random
import tkinter

INNER_CIRCLE_RADIUS = 20

COLORS = ["red", "blue", "yellow", "green", "orange", "blue", "cyan", "amber", "aqua", "azure", "burgundy", "grey", "flame"]


def visualize():
    top = tkinter.Tk()

    w = tkinter.Canvas(top, height=600, width=600)

    oc = OuterCircle(Point(300, 300), INNER_CIRCLE_RADIUS)
    oc.create_circle(20)
    oc.draw(w)
    w.pack()
    top.mainloop()


class Point:
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def length(self):
        return sqrt(self.x ** 2 + self.y ** 2)

    def euclidean_distance(self, other):
        return sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def as_tuple(self):
        return self.x, self.y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __repr__(self):
        return f"({self.x}, {self.y})"


class Circle:
    def __init__(self, mid_point, radius):
        self.mid_point = mid_point
        self.radius = radius

    def double_radius(self):
        return Circle(self.mid_point, 2 * self.radius)

    def is_inside(self, other):
        distance = self.mid_point.euclidean_distance(other.mid_point)
        return distance <= self.radius - other.radius

    def is_point_inside(self, p: Point):
        distance = self.mid_point.euclidean_distance(p)
        return distance <= self.radius

    def inner_circle_inside(self, p: Point):
        distance = self.mid_point.euclidean_distance(p)
        return distance <= (self.radius - INNER_CIRCLE_RADIUS)

    def relative_inner_circle_inside(self, p):
        explicit_point = self.left_up() + p
        return self.inner_circle_inside(explicit_point)

    def is_relative_point_inside(self, p: Point):
        explicit_point = self.left_up() + p
        return self.is_point_inside(explicit_point)

    def draw(self, canvas, color=""):
        x0, y0 = self.left_up().as_tuple()
        x1, y1 = self.right_down().as_tuple()
        canvas.create_oval(x0, y0, x1, y1, fill=color)

    def get_relative_points(self):
        for x in range(0, self.radius*2):
            for y in range(0, self.radius*2):
                if self.is_relative_point_inside(Point(x, y)):
                    yield Point(x, y)

    def get_all_points(self):
        return map(lambda x: self.left_up() + x, self.get_relative_points())

    def left_down(self):
        return Point(self.mid_point.x - self.radius, self.mid_point.y + self.radius)

    def right_down(self):
        return Point(self.mid_point.x + self.radius, self.mid_point.y + self.radius)

    def left_up(self):
        return Point(self.mid_point.x - self.radius, self.mid_point.y - self.radius)

    def right_up(self):
        return Point(self.mid_point.x + self.radius, self.mid_point.y - self.radius)

    def intersects(self, other):
        distance = self.mid_point.euclidean_distance(other.mid_point)
        return distance < self.radius + other.radius


class OuterCircle(Circle):
    def __init__(self, mid_point: Point, radius: int):
        super().__init__(mid_point, radius)
        self.inner_circles = []
        self.space = []
        self.create_space()

    def create_space(self):
        space = [[False for _ in range(self.radius * 2)] for _ in range(self.radius * 2)]
        for x in range(self.radius * 2):
            for y in range(self.radius * 2):
                space[x][y] = self.relative_inner_circle_inside(Point(x, y))
        self.space = space

    def block_space(self, inner_circle: Circle):
        self.use_space(inner_circle.double_radius())

    def block_cell(self, x, y):
        if 0 <= x < self.radius * 2 and 0 <= y < self.radius * 2:
            self.space[x][y] = False

    def use_space(self, inner_circle):
        for p in self.get_relative_points_circle(inner_circle):
            x, y = p.as_tuple()
            self.block_cell(x, y)

    def get_free_space(self):
        for x in range(self.radius * 2):
            for y in range(self.radius * 2):
                if self.space[x][y]:
                    yield Point(x, y)

    def get_inner_circle_offset_from_top_left(self, inner_circle: Circle) -> Point:
       return inner_circle.left_up() - self.left_up()

    def get_relative_points_circle(self, inner_circle: Circle):
        offset = self.get_inner_circle_offset_from_top_left(inner_circle)
        return list(map(lambda x: offset + x, inner_circle.get_relative_points()))

    def draw(self, canvas, color=""):
        for circle in self.inner_circles:
            circle.draw(canvas, "#ee" + str(secrets.token_hex(1)[1]) + "50" + str(secrets.token_hex(1)[1]))
        super().draw(canvas, color)

    def make_bigger(self):
        self.radius += 1

    def add_random_circle(self):
        free_space = list(self.get_free_space())
        if len(free_space) > 0:
            random_point = random.choice(free_space)
            random_point = random_point + self.left_up()
            new_inner_circle = OuterCircle(random_point, INNER_CIRCLE_RADIUS)
            self.inner_circles.append(new_inner_circle)
            self.block_space(new_inner_circle)
            return True
        return False

    def create_circle(self, num_circles):
        counter = 0
        while True:
            self.inner_circles = []
            self.create_space()

            counter += 1
            possible = False
            for i in range(num_circles):
                possible = self.add_random_circle()
                if not possible:
                    break
            if possible:
                break

            if counter >= 3:
                counter = 0
                self.make_bigger()


class InnerCircle(Circle):
    pass


if __name__ == '__main__':
    visualize()
    """ 
   oc = OuterCircle(Point(10, 10), 4)
    for l in oc.space:
        print(l)
    print("---")
    oc.block_space(Circle(Point(9, 9), 2))
    for l in oc.space:
        print(l)"""

