import itertools
from math import sqrt
from random import randint
import tkinter

INNER_CIRCLE_RADIUS = 20


def visualize():
    top = tkinter.Tk()

    w = tkinter.Canvas(top, height=600, width=600)

    oc = OuterCircle(Point(300, 300), INNER_CIRCLE_RADIUS)
    oc.create_circle(10)
    oc.draw(w)
    w.pack()
    top.mainloop()


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def euclidean_distance(self, other):
        return sqrt(abs(self.x - other.x) ** 2 + abs(self.y - other.y) ** 2)

    def __repr__(self):
        return f"({self.x}, {self.y})"

class Circle:
    def __init__(self, mid_point, radius):
        self.mid_point = mid_point
        self.radius = radius

    def is_inside(self, other):
        distance = self.mid_point.euclidean_distance(other.mid_point)
        return distance <= self.radius - other.radius

    def is_point_inside(self, p):
        distance = self.mid_point.euclidean_distance(p)
        return distance <= self.radius

    def draw(self, canvas):
        r = self.radius
        x = self.mid_point.x
        y = self.mid_point.y
        x0 = x - r
        y0 = y - r
        x1 = x + r
        y1 = y + r
        canvas.create_oval(x0, y0, x1, y1)

    def get_all_points(self):
        for x in range(self.mid_point.x - self.radius, self.mid_point.x + self.radius):
            for y in range(self.mid_point.y - self.radius, self.mid_point.y + self.radius):
                if self.is_point_inside(Point(x, y)):
                    yield Point(x, y)

    def left_down(self):
        return Point(self.mid_point.x - self.radius, self.mid_point.y - self.radius)

    def right_down(self):
        return Point(self.mid_point.x + self.radius, self.mid_point.y - self.radius)

    def left_up(self):
        return Point(self.mid_point.x - self.radius, self.mid_point.y + self.radius)

    def right_up(self):
        return Point(self.mid_point.x + self.radius, self.mid_point.y + self.radius)

    def intersects(self, other):
        distance = self.mid_point.euclidean_distance(other.mid_point)
        return distance < self.radius + other.radius


class OuterCircle(Circle):
    def __init__(self, mid_point: Point, radius: int):
        super().__init__(mid_point, radius)
        self.inner_circles = []
        self.space = []

    def create_space(self):
        if INNER_CIRCLE_RADIUS < self.radius:
            self.space = [[True for _ in range(INNER_CIRCLE_RADIUS, (self.radius * 2) - INNER_CIRCLE_RADIUS)] for _ in range(INNER_CIRCLE_RADIUS, (self.radius * 2) - INNER_CIRCLE_RADIUS)]

    def use_space(self, inner_circle):
        circle_x_offset = self.left_up().x + (inner_circle.midpoint.x - self.left_up().x)
        circle_y_offset = self.left_up().y - (self.left_up().y - inner_circle.midpoint.x)

    def draw(self, canvas):
        for circle in self.inner_circles:
            circle.draw(canvas)
        super().draw(canvas)

    def make_bigger(self):
        self.radius += 1

    def add_random_circle(self):
        random_x = randint(self.left_down().x + INNER_CIRCLE_RADIUS, self.right_down().x - INNER_CIRCLE_RADIUS)
        random_y = randint(self.left_down().y + INNER_CIRCLE_RADIUS, self.left_up().y - INNER_CIRCLE_RADIUS)
        rand_circle = InnerCircle(Point(random_x, random_y), INNER_CIRCLE_RADIUS)
        while not self.is_inside(rand_circle):
            random_x = randint(self.left_down().x + INNER_CIRCLE_RADIUS, self.right_down().x - INNER_CIRCLE_RADIUS)
            random_y = randint(self.left_down().y + INNER_CIRCLE_RADIUS, self.left_up().y - INNER_CIRCLE_RADIUS)
            rand_circle = InnerCircle(Point(random_x, random_y), INNER_CIRCLE_RADIUS)
        self.inner_circles.append(rand_circle)

    def is_correct(self):
        if any(map(lambda x: x[0].intersects(x[1]), list(itertools.combinations(self.inner_circles, 2)))):
            return False
        if not all(map(self.is_inside, self.inner_circles)):
            return False
        return True

    def create_circle(self, num_circles):
        correct = True
        counter = 0
        factor = 2
        while not self.is_correct() or correct:
            self.inner_circles = []
            correct = False
            counter += 1
            for i in range(num_circles):
                self.add_random_circle()
            if counter >= int(round((factor ** 2) / ((num_circles * 10) ** 2))):
                factor += 1000 / INNER_CIRCLE_RADIUS
                counter = 0
                self.make_bigger()


class InnerCircle(Circle):
    pass


if __name__ == '__main__':
    c = Circle(Point(10, 10), 2)
    print(list(c.get_all_points()))


