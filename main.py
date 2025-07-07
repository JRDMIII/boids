import pygame
from universe import Universe

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

universe = Universe(SCREEN_WIDTH, SCREEN_HEIGHT, NUM_BOIDS, BOID_COLOUR)
universe.Setup()

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
    universe.UpdateUniverse(SCREEN)

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    CLOCK.tick(60)

pygame.quit()