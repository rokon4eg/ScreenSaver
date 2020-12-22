#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import List

import pygame
import random
import math
import collections

SCREEN_DIM = (640, 480)

working = True

steps = 35
show_help = False
pause = True

hue = 0
color = pygame.Color(0)


# =======================================================================================
# класс 2-мерных векторов
# =======================================================================================
class Vec2d:

    def __init__(self, x=0, y=0):
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
        self.line.pop()

    def set_points(self):
        """функция перерасчета координат опорных точек"""
        for i in range(len(self.line)):
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
            for p_n in range(-1, len(self.line) - 1):
                pygame.draw.line(gameDisplay, color,
                                 (int(self.line[p_n].point.x), int(self.line[p_n].point.y)),
                                 (int(self.line[p_n + 1].point.x), int(self.line[p_n + 1].point.y)), width)

        elif style == "points":
            for p in self.line:
                pygame.draw.circle(gameDisplay, color,
                                   (int(p.point.x), int(p.point.y)), width)


class Knot(Polyline):

    def __init__(self, point=None, speed=None, count=35):
        super().__init__(point, speed)
        self.count = count

    @property
    def points(self):
        return [l.point for l in self.line]

    @property
    def speeds(self):
        return list(l.speed for l in self.line)

    # добавление и пересчёт координат инициируют вызов функции get_knot()
    def append(self, point, speed):
        super().append(point, speed)
        self.get_knot()

    def set_points(self):
        super().set_points()
        self.get_knot()

    def __get_point(self, points, alpha, deg=None):
        if deg is None:
            deg = len(points) - 1
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
        :param points: list[Vec2d]
        :param count: int
        :return: list[Vec2d]
        """
        points = self.points

        if len(points) < 3:
            return []
        res = []
        for i in range(-2, len(points) - 2):
            ptn = []
            ptn.append((points[i] + points[i+1]) * 0.5)
            ptn.append(points[i+1])
            ptn.append((points[i+1] + points[i+2]) * 0.5)

            res.extend(self._get_points(ptn, self.count))
        return res


# реализовать возможность удаления «опорной» точки из кривой,
# реализовать возможность отрисовки на экране нескольких кривых,
# реализовать возможность ускорения/замедления скорости движения кривой(-ых).


# =======================================================================================
# Функции для работы с векторами
# =======================================================================================

def sub(x, y):
    """"возвращает разность двух векторов"""
    return x[0] - y[0], x[1] - y[1]


def add(x, y):
    """возвращает сумму двух векторов"""
    return x[0] + y[0], x[1] + y[1]


def mul(v, k):
    """возвращает произведение вектора на число"""
    return v[0] * k, v[1] * k


def length(x):
    """возвращает длину вектора"""
    return math.sqrt(x[0] * x[0] + x[1] * x[1])


def vec(x, y):
    """возвращает пару координат, определяющих вектор (координаты точки конца вектора),
    координаты начальной точки вектора совпадают с началом системы координат (0, 0)"""
    return sub(y, x)


# =======================================================================================
# Функции отрисовки
# =======================================================================================
def draw_points(points, style="points", width=3, color=(255, 255, 255)):
    """функция отрисовки точек на экране
    :type points: list[Vec2d]
    """
    if style == "line":
        for p_n in range(-1, len(points) - 1):
            pygame.draw.line(gameDisplay, color,
                             (points[p_n].x, points[p_n].y),
                             (points[p_n + 1].x, points[p_n + 1].y), width)

    elif style == "points":
        for p in points:
            pygame.draw.circle(gameDisplay, color,
                               (p.x, p.y), width)


def draw_help():
    """функция отрисовки экрана справки программы"""
    gameDisplay.fill((50, 50, 50))
    font1 = pygame.font.SysFont("courier", 24)
    font2 = pygame.font.SysFont("serif", 24)
    data = []
    data.append(["F1", "Show Help"])
    data.append(["R", "Restart"])
    data.append(["P", "Pause/Play"])
    data.append(["Num+", "More points"])
    data.append(["Num-", "Less points"])
    data.append(["", ""])
    data.append([str(steps), "Current points"])

    pygame.draw.lines(gameDisplay, (255, 50, 50, 255), True, [
        (0, 0), (800, 0), (800, 600), (0, 600)], 5)
    for i, text in enumerate(data):
        gameDisplay.blit(font1.render(
            text[0], True, (128, 128, 255)), (100, 100 + 30 * i))
        gameDisplay.blit(font2.render(
            text[1], True, (128, 128, 255)), (200, 100 + 30 * i))


# =======================================================================================
# Функции, отвечающие за расчет сглаживания ломаной
# =======================================================================================
def get_point(points, alpha, deg=None):
    if deg is None:
        deg = len(points) - 1
    if deg == 0:
        return points[0]
    return add(mul(points[deg], alpha), mul(get_point(points, alpha, deg - 1), 1 - alpha))


def get_points(base_points, count):
    alpha = 1 / count
    res = []
    for i in range(count):
        res.append(get_point(base_points, i * alpha))
    return res


def get_knot(points, count):
    if len(points) < 3:
        return []
    res = []
    for i in range(-2, len(points) - 2):
        ptn = []
        ptn.append(mul(add(points[i], points[i + 1]), 0.5))
        ptn.append(points[i + 1])
        ptn.append(mul(add(points[i + 1], points[i + 2]), 0.5))

        res.extend(get_points(ptn, count))
    return res


def set_points(points, speeds):
    """функция перерасчета координат опорных точек"""
    for p in range(len(points)):
        points[p] = add(points[p], speeds[p])
        if points[p][0] > SCREEN_DIM[0] or points[p][0] < 0:
            speeds[p] = (- speeds[p][0], speeds[p][1])
        if points[p][1] > SCREEN_DIM[1] or points[p][1] < 0:
            speeds[p] = (speeds[p][0], -speeds[p][1])


# =======================================================================================
# Основная программа
# =======================================================================================
def run_functional_version():
    global working, pause, show_help, hue, steps
    points = []
    speeds = []

    while working:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                working = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    working = False
                if event.key == pygame.K_r:
                    points = []
                    speeds = []
                if event.key == pygame.K_p:
                    pause = not pause
                if event.key == pygame.K_KP_PLUS:
                    steps += 1
                if event.key == pygame.K_KP_MINUS:
                    steps -= 1 if steps > 1 else 0
                if event.key == pygame.K_F1:
                    show_help = not show_help

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in (1, 4):
                    points.append(event.pos)
                    speeds.append((random.random() * 2, random.random() * 2))
                else:
                    points.pop()
                    speeds.pop()

        gameDisplay.fill((0, 0, 0))
        hue = (hue + 1) % 360
        color.hsla = (hue, 100, 50, 100)
        draw_points(points)
        draw_points(get_knot(points, steps), "line", 3, color)
        if not pause:
            set_points(points, speeds)
        if show_help:
            draw_help()

        pygame.display.flip()


def run_class_version():
    global working, pause, steps, show_help, hue

    point = Vec2d(0, 0)
    speed = Vec2d(0, 0)
    knot = Knot(point, speed)

    while working:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                working = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    working = False
                if event.key == pygame.K_r:
                    point = Vec2d(0, 0)
                    speed = Vec2d(0, 0)
                    knot=Knot(point, speed)
                    # ToDo
                    # points = []
                    # speeds = []
                if event.key == pygame.K_p:
                    pause = not pause
                if event.key == pygame.K_KP_PLUS:
                    steps += 1
                if event.key == pygame.K_KP_MINUS:
                    steps -= 1 if steps > 1 else 0
                if event.key == pygame.K_F1:
                    show_help = not show_help

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in (1, 4):
                    point = Vec2d(*event.pos)
                    speed = Vec2d(random.random() * 2, random.random() * 2)
                    knot.append(point,speed)
                    # points.append(event.pos)
                    # speeds.append((random.random() * 2, random.random() * 2))
                else:
                    knot.delete()
                    # points.pop()
                    # speeds.pop()

        gameDisplay.fill((0, 0, 0))
        hue = (hue + 1) % 360
        color.hsla = (hue, 100, 50, 100)

        # points: list[Vec2d] = list(l.point for l in knot.line)
        # speeds: list[Vec2d] = list(l.speed for l in knot.line)

        draw_points(knot.points)
        draw_points(knot.get_knot(), "line", 3, color)
        if not pause:
            knot.set_points()
        if show_help:
            draw_help()

        pygame.display.flip()


if __name__ == "__main__":
    pygame.init()
    gameDisplay = pygame.display.set_mode(SCREEN_DIM)
    pygame.display.set_caption("MyScreenSaver")

    # run_functional_version()

    run_class_version()

    pygame.display.quit()
    pygame.quit()
    exit(0)
