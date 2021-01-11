#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pygame
import random
import math
import collections


# ============================================================================
# класс 2-мерных векторов
# =======================================================================================
class Vec2d:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, b):
        """возвращает сумму двух векторов"""
        return Vec2d(self.x + b.x, self.y + b.y)

    def __sub__(self, b):
        """возвращает разность двух векторов"""
        return Vec2d(self.x - b.x, self.y - b.y)

    def __mul__(self, k):
        return Vec2d(self.x * k, self.y * k)

    # метод возвращает текущие координаты вектора.
    def int_pair(self):
        return self.x, self.y

    # вычисляет длину вектора
    def len(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)


# =======================================================================================
# класс замкнутых ломаных
# =======================================================================================
class Polyline:
    point_speed = collections.namedtuple('point_speed', 'point, speed')
    line: list[point_speed]
    ext_line: list[Vec2d]

    SCREEN_DIM = (1024, 768)

    def __init__(self, point, speed):
        """
        :type point: Vec2d
        :type speed: Vec2d
        """
        self.line = [self.point_speed(point, speed)]
        self.gameDisplay = pygame.display.set_mode(self.SCREEN_DIM)

    def append(self, point, speed):
        """метод добавление в ломаную точки (Vec2d) c её скоростью
        :type speed: Vec2d
        :type point: Vec2d
        """
        self.line.append(self.point_speed(point, speed))

    def delete(self):
        """метод удаления из ломаной последней точки (Vec2d)"""
        if self.line.__len__() != 0:
            self.line.pop()

    def set_points(self):
        """функция перерасчета координат опорных точек"""
        for i in range(self.line.__len__()):
            point = self.line[i].point + self.line[i].speed
            x, y = point.int_pair()
            self.line[i] = self.point_speed(point, self.line[i].speed)
            if x > self.SCREEN_DIM[0] or x < 0:
                self.line[i].speed.x *= -1
            if y > self.SCREEN_DIM[1] or y < 0:
                self.line[i].speed.y *= -1

    # =======================================================================================
    # Функции отрисовки
    # =======================================================================================
    def draw_points(self, points, style="points", width=3, color=(255, 255, 255)):
        """функция отрисовки точек на экране
        :type points: list[Vec2d]
        """
        if style == "line":
            for p_n in range(-1, points.__len__() - 1):
                pygame.draw.line(self.gameDisplay, color,
                                 (points[p_n].int_pair()),
                                 (points[p_n + 1].int_pair()), width)
        elif style == "points":
            for p in points:
                pygame.draw.circle(self.gameDisplay, color,
                                   (p.int_pair()), width)

    def draw_help(self, active_knot):
        """функция отрисовки экрана справки программы"""
        self.gameDisplay.fill((50, 50, 50))
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
        data.append(["1-9", "Select line for modify"])
        data.append([str(active_knot + 1), "Current active line number "])
        data.append([str(knot_list[active_knot].count), "Current points"])

        pygame.draw.lines(self.gameDisplay, (255, 50, 50, 255), True, [
            (0, 0), (800, 0), (800, 600), (0, 600)], 5)
        for i, text in enumerate(data):
            self.gameDisplay.blit(font1.render(
                text[0], True, (128, 128, 255)), (100, 100 + 30 * i))
            self.gameDisplay.blit(font2.render(
                text[1], True, (128, 128, 255)), (300, 100 + 30 * i))


class Knot(Polyline):

    def __fill(self):
        for _ in range(2):
            speed = Vec2d(random.random() * 2, random.random() * 2)
            point = Vec2d(random.randint(0, self.SCREEN_DIM[0]), random.randint(0, self.SCREEN_DIM[1]))
            self.append(point, speed)

    def __init__(self, point=None, speed=None, count=35, isfill=False):
        if speed is None:
            speed = Vec2d(random.random() * 2, random.random() * 2)
        if point is None:
            point = Vec2d(random.randint(0, self.SCREEN_DIM[0]), random.randint(0, self.SCREEN_DIM[1]))
        super().__init__(point, speed)
        self.ext_line = []
        self.count = count
        self.hue = random.randint(1, 1000) % 360

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

    def __get_point(self, ptn, alpha, deg=None):
        if deg is None:
            deg = ptn.__len__() - 1
        if deg == 0:
            return ptn[0]
        return ptn[deg] * alpha + self.__get_point(ptn, alpha, deg - 1) * (1 - alpha)

    def _get_points(self, ptn, count):
        """
        :rtype: list[Vec2d]
        """
        alpha = 1 / count
        res = []
        for i in range(count):
            res.append(self.__get_point(ptn, i * alpha))
        return res

    def get_knot(self):
        """
        :return: list[Vec2d]
        """
        base_points = self.points
        res = []

        if base_points.__len__() >= 3:
            for i in range(-2, base_points.__len__() - 2):
                ptn = [(base_points[i] + base_points[i + 1]) * 0.5, base_points[i + 1],
                       (base_points[i + 1] + base_points[i + 2]) * 0.5]
                res.extend(self._get_points(ptn, self.count))
        self.ext_line = res


class Draw:
    MAX_KNOTS = 9

    def __init__(self, working=True):

        self.working = working
        self.pause = False
        self.show_help = False
        self._active_knot = 1
        self.line_key = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7,
                         pygame.K_8,
                         pygame.K_9]

    def do_event(self, knot):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.working = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.working = False

                if event.key == pygame.K_r:
                    knot.__init__()
                if event.key == pygame.K_p:
                    self.pause = not self.pause

                # add line
                if event.key == pygame.K_KP_PLUS:
                    if knot_list.__len__() < self.MAX_KNOTS:
                        knot_list.append(Knot(isfill=True))
                        self._active_knot = knot_list.__len__()

                # delete line
                if event.key == pygame.K_KP_MINUS:
                    if knot_list.__len__() > 1:
                        active = self._active_knot
                        knot_list.pop(active - 1)
                        Len = knot_list.__len__()
                        if active > (Len):
                            self._active_knot = Len

                # select active line
                if event.key in self.line_key:
                    index = self.line_key.index(event.key)
                    if index < knot_list.__len__():
                        self._active_knot = index + 1

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
                    if self.pause: knot.get_knot()
                elif event.button == 5:
                    knot.count -= 1 if knot.count > 1 else 0
                    if self.pause: knot.get_knot()

    def do_draw(self, knot_list):
        color = pygame.Color(0)
        while self.working:
            self.do_event(knot_list[self._active_knot - 1])
            knot_list[self._active_knot - 1].gameDisplay.fill((0, 0, 0))
            for knot in knot_list:
                color.hsla = (knot.hue, 100, 50, 100)
                if not self.pause:
                    knot.set_points()
                knot.draw_points(knot.points)
                knot.draw_points(knot.ext_line, "line", 3, color)
                if self.show_help:
                    knot.draw_help(self._active_knot - 1)
            pygame.display.flip()


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("MyScreenSaver")

    knot = Knot(isfill=True)
    knot_list = [knot]

    draw = Draw()
    draw.do_draw(knot_list)

    pygame.display.quit()
    pygame.quit()
    exit(0)
