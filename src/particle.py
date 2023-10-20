import numpy as np
from src.graphics import *
import random
import math

class Particle:
    """
    x, y: coordinates of bottom left corner
    """
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.p1 = Point(x, y)
        self.p2 = Point(x+w, y+h)
        self.rect = Rectangle(self.p1, self.p2)
        self.theta = random.random() * 2 * np.pi

    def turn_around(self):
        self.theta = self.theta % (2 * np.pi)

        if 0 <= self.theta < np.pi / 2:
            self.theta = np.pi - self.theta
        elif np.pi / 2 <= self.theta < np.pi:
            self.theta = self.theta - np.pi
        elif np.pi <= self.theta < 3 * np.pi / 2:
            self.theta = self.theta - np.pi
        else:
            self.theta = 2 * np.pi - self.theta

    def update(self, screen_w, screen_h):
        self.theta += random.random() * 0.1 - 0.1 / 2

        new_x = self.x + np.cos(self.theta) * 0.5
        new_y = self.y + np.sin(self.theta) * 0.5

        if new_x < 0 or new_y < 0 or new_x >= screen_w or new_y >= screen_h:
            self.turn_around()
            return

        self.x = new_x
        self.y = new_y
        self.p1 = Point(new_x, new_y)
        self.p2 = Point(new_x + self.w, new_y + self.h)
        self.rect = self.rect = Rectangle(self.p1, self.p2)

    def draw(self, win):
        rect = Rectangle(Point(self.x, self.y), Point(self.x + self.w, self.y + self.h))
        rect.draw(win)

    def distance_to(self, other_particle):
        """
        Calculate the Euclidean distance between this particle and another particle
        """
        dx = self.x - other_particle.x
        dy = self.y - other_particle.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def find_k_closest_particles(self, particles, k):
        """
        Find the k closest particles to this particle
        """
        distances = [(particle, self.distance_to(particle)) for particle in particles]
        closest_particles = sorted(distances, key=lambda item: item[1])[:k]
        k_closest_particles = [particle for particle, _ in closest_particles]

        return k_closest_particles
