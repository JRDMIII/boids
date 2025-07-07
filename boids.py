
import pygame
import random as r
import math

class Boid():
    def __init__(self, x, y, bounds, speed=1, colour=(255, 255, 255)):
        """Constructor for the Boid class"""

        self.id = str(r.randint(0, 2000))

        # Coordinates of the boid
        self.position = pygame.Vector2(x, y)

        # Lambda function generates random variance number
        variance = lambda: r.randint(-3, 3)
        self.colour = (colour[0] + variance(), colour[1] + variance(), colour[2] + variance())

        # Generate random angles for sin and cos
        angle = r.randint(0, 360)

        # Calculate sin and cos of the angle multiplied by speed (using parametric equations)
        self.max_speed = speed
        self.velocity = pygame.Vector2(speed * math.cos(angle), speed * math.sin(angle))
        self.acceleration = pygame.Vector2(0, 0)

        self.bounds = bounds # Bounds of the screen

    def ApplySeparationForce(self, neighbours):
        force = pygame.Vector2()
        
        # Ignore function if there are no neighbours
        if len(neighbours) == 0: return

        for n in neighbours:
            n: Boid

            displacement = self.position - n.position
            distance = self.position.distance_to(n.position)

            # We scale the separation force applied by the distance to the boid
            if distance != 0:
                displacement /= distance
            force += displacement
        
        self.ApplyForce(force)

    def UpdatePosition(self):
        """Update the position of the boid"""
        self.velocity += self.acceleration
        
        # If the boid begins to move too fast, reduce scalar speed to max_speed
        if self.velocity.length() > self.max_speed:
            self.velocity.scale_to_length(self.max_speed)
        
        self.position += self.velocity

        # Reset acceleration value ready for physics calculations next frame
        self.acceleration *= 0

        # Make boid wrap around the screen
        self.position.x %= self.bounds[0]
        self.position.y %= self.bounds[1]
    
    def ApplyForce(self, force:pygame.Vector2):
        self.acceleration += force

    def Draw(self, screen):
        """Draw the boid on the given screen."""
        pygame.draw.circle(screen, self.colour, (int(self.position[0]), int(self.position[1])), 5)

    def Update(self, neighbours, screen):
        # Apply all forces from rules
        self.ApplySeparationForce(neighbours)

        # Update position using newly updated acceleration
        self.UpdatePosition()

        # Draw boid to the screen
        self.Draw(screen)