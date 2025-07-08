
import pygame
import random as r
import math

class Boid():
    def __init__(self, x:int, y:int, bounds:list, speed:int=1, colour:tuple=(255, 255, 255)):
        """Constructor for the Boid class"""

        self.id = str(r.randint(0, 2000))

        # Coordinates of the boid
        self.position = pygame.Vector2(x, y)

        # Lambda function generates random variance number
        variance = lambda: r.randint(-30, 30)
        self.colour = (
            min(colour[0] + variance(), 255),
            min(colour[1] + variance(), 255),
            min(colour[2] + variance(), 255)
        )

        # Generate random angles for sin and cos
        angle = r.randint(0, 360)

        # Calculate sin and cos of the angle multiplied by speed (using parametric equations)
        self.max_speed = speed
        self.velocity = pygame.Vector2(speed * math.cos(angle), speed * math.sin(angle))
        self.acceleration = pygame.Vector2(0, 0)
        self.max_force = 0.05

        self.bounds = bounds # Bounds of the screen

    def _ApplyRuleForces(self, neighbours:list['Boid']):
        separation_force = pygame.Vector2()
        alignment_force = pygame.Vector2()
        
        num = len(neighbours)

        # Ignore function if there are no neighbours
        if num == 0: return

        for n in neighbours:
            n: Boid

            if n == self: continue

            # Adding averaged velocity to the alignment force
            alignment_force += n.velocity / num

            displacement = self.position - n.position
            distance = self.position.distance_to(n.position)

            # We scale the separation force applied by the distance to the boid
            if distance != 0:
                displacement /= distance
            separation_force += displacement / num
        
        # Normalising the alignment force so that it doesn't exceed max speed
        if alignment_force.length() != 0:
            alignment_force = alignment_force.normalize() * self.max_speed
            alignment_force -= self.velocity
            if alignment_force.length() != 0:
                alignment_force = alignment_force.clamp_magnitude(self.max_force)

        if separation_force.length() != 0:
            separation_force = separation_force.normalize() * self.max_speed
            separation_force -= self.velocity
            if separation_force.length() != 0:
                separation_force = separation_force.clamp_magnitude(self.max_force)
        
        self._ApplyForces(separation_force, alignment_force)

    def _UpdatePosition(self):
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
    
    def _ApplyForces(self, *forces:list[pygame.Vector2]):
        for f in forces:
            self.acceleration = self.acceleration + f

    def _Draw(self, screen):
        """Draw the boid on the given screen."""
        # Calculating direction of the boid
        angle = math.atan2(self.velocity.y, self.velocity.x)

        # Calculate the points of the triangle
        size = 5

        points = [
            (size, 0),
            (-size / 2, -size / 2),
            (-size / 2, size / 2)
        ]

        new_points = []

        # Rotating the points to match the direction
        for x, y in points:
            rotated_x = x * math.cos(angle) - y * math.sin(angle)
            rotated_y = x * math.sin(angle) + y * math.cos(angle)

            new_points.append((self.position.x + rotated_x, self.position.y + rotated_y))

        pygame.draw.polygon(screen, self.colour, new_points)

    def Update(self, neighbours:list['Boid'], screen):
        # Apply all forces from rules
        self._ApplyRuleForces(neighbours)

        # Update position using newly updated acceleration
        self._UpdatePosition()

        # Draw boid to the screen
        self._Draw(screen)