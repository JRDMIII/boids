import pygame
from boids import Boid
import random

# Setting up pygame environment
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CLOCK = pygame.time.Clock()

# Setting up the display
pygame.display.set_caption("Boids")
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

NUM_BOIDS = 10  # Number of boids to create
BOID_COLOUR = (176, 224, 230)

boids = []
for i in range(NUM_BOIDS):
    # Create a boid with random position and default speed and color
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT)
    new_boid = Boid(x, y, colour=BOID_COLOUR, bounds=(SCREEN_WIDTH, SCREEN_HEIGHT))
    boids.append(new_boid)

# Bool to control the main loop
running = True

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the background of the screen with black
    SCREEN.fill((0, 0, 0))

    # Update game content here
    for boid in boids:
        boid: Boid
        boid.UpdatePosition()
        boid.Draw(SCREEN)

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    CLOCK.tick(60)

pygame.quit()