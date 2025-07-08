from boids import Boid
import random
import math
from collections import defaultdict

class Universe:
    def __init__(self, width, height, boid_number, boid_colour):
        self.width = width
        self.height = height
        self.boid_number = boid_number
        self.boid_colour = boid_colour
        self.boids = []

        self.partition_size = 200
        self.partitions = defaultdict(list)
    
    def Setup(self, max_speed):
        """Create all boids and add them to the list of boids"""
        for _ in range(self.boid_number):
            # Create a boid with random position and default speed and color
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)

            new_boid = Boid(x, y, 
                speed=max_speed, 
                colour=self.boid_colour, 
                bounds=(self.width, self.height)
            )

            self.boids.append(new_boid)
        
    def UpdatePartitions(self):
        """Update what partition each boid is in"""

        # Clear all previous positions
        self.partitions.clear()

        for b in self.boids:
            b: Boid

            # Creating key for the boid
            cell_x = int(b.position.x // self.partition_size)
            cell_y = int(b.position.y // self.partition_size)
            key = (cell_x, cell_y)

            # Checking if we have that key in the section
            if key not in self.partitions:
                self.partitions[key] = []
            self.partitions[key].append(b)
            
    def GetNeighbours(self, boid:Boid, radius=30):
        neighbours = []

        # Getting grid coordinates for current boid
        cell_x = int(boid.position.x // self.partition_size)
        cell_y = int(boid.position.y // self.partition_size)

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                key = (cell_x + dx, cell_y + dy)
                # Loop through all boids in that partition and check if they are within the radius
                for b in self.partitions[key]:
                    if b == boid: continue

                    b: Boid
                    dist = math.sqrt((boid.position.x - b.position.x)**2 + (boid.position.y - b.position.y)**2)
                    if dist <= radius:
                        neighbours.append(b)

        return neighbours
            
    def UpdateUniverse(self, screen):
        self.UpdatePartitions()
        for b in self.boids:
            b: Boid
            neighbours = self.GetNeighbours(b)
            b.Update(neighbours, screen)
