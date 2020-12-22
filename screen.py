#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pygame
import random
import math
import collections

SCREEN_DIM = (1024, 768)


# working = True

# steps = 35
# show_help = False
# pause = True

# hue = 0


# =======================================================================================
# класс 2-мерных векторов
# =======================================================================================
class Vec2d:

    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    # методы для основных математических операций, необходимых для работы с вектором
    def __add__(self, b):
        """возвращает сумму двух векторов"""
        return Vec2d(self.x + b.x, self.y + b.y)

    def __sub__(self, b):
        """возвращает разность двух векторов"""
        return Vec2d(self.x - b.x, self.y - b.y)

    def __mul__(self, k):
        return Vec2d(self.x * k, self.y * k)

    # добавить возможность вычислять длину вектора с использованием функции

    # метод который возвращает кортеж из двух целых чисел (текущие координаты вектора).
    def int_pair(self):
        return self.x, self.y

    def len(self):
        """возвращает длину вектора"""
        return math.sqrt(self.x ** 2 + self.y ** 2)


# =======================================================================================
# класс замкнутых ломаных
# =======================================================================================
point_speed = collections.namedtuple('point_speed', 'point, speed')


class Polyline:
    line: list[point_speed]

    def __init__(self, point, speed):
        """
        :type point: Vec2d
        :type speed: Vec2d
        """
        self.line = [point_speed(point, speed)]

    def append(self, point, speed):
        """метод добавление в ломаную точки (Vec2d) c её скоростью
        :type speed: Vec2d
        :type point: Vec2d
        """
        self.line.append(point_speed(point, speed))

    def delete(self):
        """метод удаления из ломаной последней точки (Vec2d)"""
        if self.line.__len__() !=0:
            self.line.pop()

    def set_points(self):
        """функция перерасчета координат опорных точек"""
        for i in range(self.line.__len__()):
            point = self.line[i].point + self.line[i].speed
            x, y = point.x, point.y
            self.line[i] = point_speed(point, self.line[i].speed)
            if x > SCREEN_DIM[0] or x < 0:
                self.line[i].speed.x *= -1
            if y > SCREEN_DIM[1] or y < 0:
                self.line[i].speed.y *= -1

    def draw_points(self, style="points", width=3, color=(255, 255, 255)):
        """функция отрисовки точек на экране"""
        if style == "line":
            for p_n in range(-1, self.line.__len__() - 1):
                pygame.draw.line(gameDisplay, color,
                                 (int(self.line[p_n].point.x), int(self.line[p_n].point.y)),
                                 (int(self.line[p_n + 1].point.x), int(self.line[p_n + 1].point.y)), width)

        elif style == "points":
            for p in self.line:
                pygame.draw.circle(gameDisplay, color,
                                   (int(p.point.x), int(p.point.y)), width)


class Knot(Polyline):

    def __fill(self):
        for _ in range(2):
            speed = Vec2d(random.random() * 2, random.random() * 2)
            point = Vec2d(random.randint(0, SCREEN_DIM[0]),random.randint(0, SCREEN_DIM[1]))
            self.append(point, speed)
        # speed = Vec2d(random.random() * 2, random.random() * 2)
        # self.append(Vec2d(100, 100), speed)

    def __init__(self, point=Vec2d(0, 0), speed=Vec2d(0, 0), count=35, hue=0, isfill=False):
        super().__init__(point, speed)
        self.count = count
        self.hue = random.randint(1,1000) % 360

        if isfill:
            self.__fill()

    @property
    def points(self):
        return [line.point for line in self.line]

    @property
    def speeds(self):
        return [line.speed for line in self.line]

    # добавление и пересчёт координат инициируют вызов функции get_knot()
    def append(self, point, speed):
        super().append(point, speed)
        self.get_knot()

    def set_points(self):
        super().set_points()
        self.get_knot()

    def __get_point(self, points, alpha, deg=None):
        if deg is None:
            deg = points.__len__() - 1
        if deg == 0:
            return points[0]
        return points[deg] * alpha + self.__get_point(points, alpha, deg - 1) * (1 - alpha)

    def _get_points(self, base_points, count):
        """
        :rtype: list[Vec2d]
        """
        alpha = 1 / count
        res = []
        for i in range(count):
            res.append(self.__get_point(base_points, i * alpha))
        return res

    def get_knot(self):
        """
        :return: list[Vec2d]
        """
        points = self.points

        if points.__len__() < 3:
            return []
        res = []
        for i in range(-2, points.__len__() - 2):
            ptn = []
            ptn.append((points[i] + points[i + 1]) * 0.5)
            ptn.append(points[i + 1])
            ptn.append((points[i + 1] + points[i + 2]) * 0.5)

            res.extend(self._get_points(ptn, self.count))
        return res


# реализовать возможность удаления «опорной» точки из кривой,
# реализовать возможность отрисовки на экране нескольких кривых,
# реализовать возможность ускорения/замедления скорости движения кривой(-ых).


# =======================================================================================
# Функции для работы с векторами
# =======================================================================================
def len(x):
    """возвращает длину вектора"""
    return math.sqrt(x[0] * x[0] + x[1] * x[1])

def vec(x, y):
    """возвращает пару координат, определяющих вектор (координаты точки конца вектора),
    координаты начальной точки вектора совпадают с началом системы координат (0, 0)"""
    return sub(y, x)


class Draw:

    def __init__(self, working=True, pause=True):
        self.working = working
        self.pause = pause
        self.show_help = False
        self._active_knot = 0

    # =======================================================================================
    # Функции отрисовки
    # =======================================================================================
    @staticmethod
    def draw_points(points, style="points", width=3, color=(255, 255, 255)):
        """функция отрисовки точек на экране
        :type points: list[Vec2d]
        """
        if style == "line":
            for p_n in range(-1, points.__len__() - 1):
                pygame.draw.line(gameDisplay, color,
                                 (points[p_n].x, points[p_n].y),
                                 (points[p_n + 1].x, points[p_n + 1].y), width)

        elif style == "points":
            for p in points:
                pygame.draw.circle(gameDisplay, color,
                                   (p.x, p.y), width)

    def draw_help(self):
        """функция отрисовки экрана справки программы"""
        gameDisplay.fill((50, 50, 50))
        font1 = pygame.font.SysFont("courier", 24)
        font2 = pygame.font.SysFont("serif", 24)
        data = []
        data.append(["F1", "Show Help"])
        data.append(["R", "Restart"])
        data.append(["P", "Pause/Play"])
        data.append(["LMB click", "Add basic point"])
        data.append(["RMB click", "Delete basic point"])
        data.append(["scroll up", "More points"])
        data.append(["scroll down", "Less points"])
        data.append(["Num+", "Add line"])
        data.append(["Num-", "Delete line"])
        data.append(["0-9", "Select line for modify"])
        data.append([str(self._active_knot), "Current active line number "])
        data.append([str(knot_list[self._active_knot].count), "Current points"])

        pygame.draw.lines(gameDisplay, (255, 50, 50, 255), True, [
            (0, 0), (800, 0), (800, 600), (0, 600)], 5)
        for i, text in enumerate(data):
            gameDisplay.blit(font1.render(
                text[0], True, (128, 128, 255)), (100, 100 + 30 * i))
            gameDisplay.blit(font2.render(
                text[1], True, (128, 128, 255)), (300, 100 + 30 * i))

    def do_event(self, knot):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.working = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.working = False
                if event.key == pygame.K_r:
                    knot.__init__()# = Knot(Vec2d(0, 0), Vec2d(0, 0))
                if event.key == pygame.K_p:
                    self.pause = not self.pause

                # add line
                if event.key == pygame.K_KP_PLUS:
                    if knot_list.__len__() <= 10:
                        knot_list.append(Knot(isfill=True))
                        self._active_knot = knot_list.__len__() - 1

                # delete line
                if event.key == pygame.K_KP_MINUS:
                    if knot_list.__len__() > 1:
                        active = self._active_knot
                        knot_list.pop(active)
                        Len = knot_list.__len__()
                        if active > (Len - 1):
                            self._active_knot = Len - 1

                # select active line
                if event.key in key:
                    index = key.index(event.key)
                    if index < knot_list.__len__():
                        self._active_knot = index

                if event.key == pygame.K_F1:
                    self.show_help = not self.show_help

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    point = Vec2d(*event.pos)
                    speed = Vec2d(random.random() * 2, random.random() * 2)
                    knot.append(point, speed)
                elif event.button == 3:
                    knot.delete()
                elif event.button == 4:
                    knot.count += 1
                elif event.button == 5:
                    knot.count -= 1 if knot.count > 1 else 0

    def do_draw(self, knot_list):
        hue = 0
        color = pygame.Color(0)
        while self.working:
            self.do_event(knot_list[self._active_knot])
            gameDisplay.fill((0, 0, 0))
            for knot in knot_list:
                if not self.pause:
                    color.hsla = (knot.hue, 100, 50, 100)
                    knot.set_points()
                # self.draw_points(knot.points)
                self.draw_points(knot.get_knot(), "line", 3, color)
                if self.show_help:
                    self.draw_help()
            pygame.display.flip()


if __name__ == "__main__":
    pygame.init()
    gameDisplay = pygame.display.set_mode(SCREEN_DIM)
    pygame.display.set_caption("MyScreenSaver")
    key = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]
    draw = Draw(pause=False)
    knot = Knot(isfill=True)
    knot_list = [knot]

    draw.do_draw(knot_list)

    pygame.display.quit()
    pygame.quit()
    exit(0)
