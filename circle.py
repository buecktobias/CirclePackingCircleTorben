from math import sqrt
import random
import tkinter

INNER_CIRCLE_RADIUS = 1
AMOUNT_CIRCLES = 1500
BIGGER_FACTOR = 1

COLORS = ["red", "blue", "yellow", "green", "orange", "blue", "cyan", "amber", "aqua", "azure", "burgundy", "grey", "flame"]

SCALE = 8


def visualize():
    top = tkinter.Tk()

    w = tkinter.Canvas(top, height=1200, width=1700)

    oc = OuterCircle(Point(340, 500), round(INNER_CIRCLE_RADIUS * (sqrt(AMOUNT_CIRCLES))))
    oc.create_circle(AMOUNT_CIRCLES)
    els = oc.draw(w)

    for el in els:
        w.scale(el, 300, 500, SCALE, SCALE)
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

    def __hash__(self):
        return hash((self.x, self.y))

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __repr__(self):
        return f"({self.x}, {self.y})"


class Circle:
    def __init__(self, mid_point, radius, color=""):
        self.mid_point = mid_point
        self.radius = radius
        self.color = color

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
        if self.color == "":
            return canvas.create_oval(x0, y0, x1, y1, fill=color)
        else:
            return canvas.create_oval(x0, y0, x1, y1, fill=self.color)

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
        els = []
        for circle in self.inner_circles:
            diff = self.mid_point.euclidean_distance(circle.mid_point)
            r0 = max(0, 255 - (20 * sqrt(diff)))

            r1 = min(255, r0 + 60)

            g0 = max(0, 180 - (35 * sqrt(diff)))
            b0 = max(0, 160 - (35 * sqrt(diff)))

            g1 = g0 + 50
            b1 = b0 + 50


            els.append(circle.draw(canvas, random_color(r0, r1, g0, g1, b0, b1)))
        els.append(super().draw(canvas, color))
        return els

    def make_bigger(self, radius=1):
        self.radius += radius

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


    def create_plus(self, c):
        amount_plus_circles = 7
        P1 = self.mid_point - Point(0, INNER_CIRCLE_RADIUS * (amount_plus_circles - 1))
        ps_vertical = [P1] + [P1 + Point(0, i * INNER_CIRCLE_RADIUS * 2) for i in range(1, amount_plus_circles)]
        Q1 = self.mid_point - Point(INNER_CIRCLE_RADIUS * (amount_plus_circles - 1), 0)
        qs_horizontal = [Q1] + [Q1 + Point(i * INNER_CIRCLE_RADIUS * 2, 0) for i in range(1, amount_plus_circles) if i != round((amount_plus_circles - 1) / 2)]
        all_plus_points = ps_vertical + qs_horizontal
        cs = list(map(lambda x: Circle(x, INNER_CIRCLE_RADIUS, c()), all_plus_points))
        for c in cs:
            self.block_space(c)
            self.inner_circles.append(c)

    def create_l(self, c):
        PLUS_DIFF = 7
        down_n = 8
        side_n = 5
        mid_l = self.mid_point - Point(PLUS_DIFF * INNER_CIRCLE_RADIUS * 2, 0)
        top_l = mid_l - Point(0, round((down_n - 1) / 2 * INNER_CIRCLE_RADIUS * 2))  # ich weiß das mal zwei und geteilt durch zwei sich aufheben
        ls_vertical = [top_l] + [top_l + Point(0, INNER_CIRCLE_RADIUS * i * 2) for i in range(1, down_n)]
        down_l = ls_vertical[-1]
        ls_horizontal = [down_l] + [down_l + Point(INNER_CIRCLE_RADIUS * i * 2, 0) for i in range(1, side_n)]

        all_ps = ls_horizontal + ls_vertical
        cs = list(map(lambda x: Circle(x, INNER_CIRCLE_RADIUS, c()), all_ps))
        for c in cs:
            self.block_space(c)
            self.inner_circles.append(c)

    def create_t(self, c):
        hori_n = 7
        vert_n = 8

        top_left_t = self.mid_point + Point(INNER_CIRCLE_RADIUS * 2 * 4, - INNER_CIRCLE_RADIUS * 2 * 3)
        ls_hori = [top_left_t] + [top_left_t + Point(INNER_CIRCLE_RADIUS * i * 2, 0) for i in range(1, hori_n)]

        mid_n = round((hori_n - 1) / 2)
        top_mid = top_left_t + Point(INNER_CIRCLE_RADIUS * mid_n * 2, 0)
        ls_vert = [top_mid + Point(0, INNER_CIRCLE_RADIUS * i * 2) for i in range(1, vert_n)]

        all_ps =  ls_hori + ls_vert
        cs = list(map(lambda x: Circle(x, INNER_CIRCLE_RADIUS, c()), all_ps))
        for c in cs:
            self.block_space(c)
            self.inner_circles.append(c)



    def create_tola(self):
        c = lambda: random_color(0, 20, 120, 200, 0, 20)
        self.create_plus(c)
        self.create_l(c)
        self.create_t(c)


    def create_circle(self, num_circles):
        counter = 0
        while True:
            self.inner_circles = []
            self.create_space()
            self.create_tola()
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
                self.make_bigger(BIGGER_FACTOR)




class InnerCircle(Circle):
    pass


def to_hex(num):
    h = hex(num)[2:]
    if len(h) < 2:
        return "0" + h
    return h


def random_color(from_r, to_r, from_g, to_g, from_b, to_b):
    r = random.randint(round(from_r), round(to_r))
    g = random.randint(round(from_g), round(to_g))
    b = random.randint(round(from_b), round(to_b))
    rgb = [r, g, b]
    return "#" + "".join(map(to_hex, rgb))


if __name__ == '__main__':
    print(random_color(0,255,0,255,0,255))
    visualize()
    """ 
   oc = OuterCircle(Point(10, 10), 4)
    for l in oc.space:
        print(l)
    print("---")
    oc.block_space(Circle(Point(9, 9), 2))
    for l in oc.space:
        print(l)"""

