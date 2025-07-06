
import pygame
import random as r

class Boid():
    def __init__(self, x, y, bounds, speed=(1, 1), colour=(255, 255, 255)):
        """Constructor for the Boid class"""

        # Coordinates of the boid 
        self.x, self.y = x, y

        # Lambda function generates random variance number
        variance = lambda: r.randint(-3, 3)
        self.colour = (colour[0] + variance(), colour[1] + variance(), colour[2] + variance())

        self.vx, self.vy = speed
        self.bounds = bounds # Bounds of the screen

    def UpdatePosition(self):
        """Update the position of the boid based on its velocity."""
        self.x = (self.x + self.vx) % self.bounds[0]
        self.y = (self.y + self.vy) % self.bounds[1]

    def Draw(self, screen):
        """Draw the boid on the given screen."""
        pygame.draw.circle(screen, self.colour, (int(self.x), int(self.y)), 5)