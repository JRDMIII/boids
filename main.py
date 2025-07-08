import pygame
from universe import Universe

# Setting up pygame environment
pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 1000
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 10)

# Setting up the display
pygame.display.set_caption("Boids")
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

NUM_BOIDS = 200  # Number of boids to create
BOID_COLOUR = (176, 224, 230)

universe = Universe(SCREEN_WIDTH, SCREEN_HEIGHT, NUM_BOIDS, BOID_COLOUR)
universe.Setup(2)

def CalculateAverageFPS(average_fps, next_fps):
    total = average_fps[0] * average_fps[1]
    total += next_fps
    total /= average_fps[1] + 1
    return total, average_fps[1] + 1

timed = False
total_time = 20
start_time = pygame.time.get_ticks()

# Bool to control the main loop
running = True

def PrintResults(avg):
    print(f"Number of boids: {NUM_BOIDS}")
    print(f"Screen Size: {SCREEN_WIDTH}×{SCREEN_HEIGHT}")
    print(f"Average FPS was: {avg[0]}")

while running:
    avg = (0, 0)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            PrintResults(avg)
            running = False

    # Fill the background of the screen with black
    SCREEN.fill((10, 10, 10))

    # Update game content here
    universe.UpdateUniverse(SCREEN)

    fps = CLOCK.get_fps()
    fps_text = FONT.render(f"FPS: {fps:.2f}", True, (255, 255, 255))
    SCREEN.blit(fps_text, (10, 10))
    avg = CalculateAverageFPS(avg, fps)

    # Update the display
    pygame.display.flip()

    if timed:
        elapsed = (pygame.time.get_ticks() - start_time) / 1000
        if elapsed >= total_time:
            PrintResults(avg)
            running = False
    
    # Cap frame rate at 165 (For 165hz screen)
    CLOCK.tick(165)

pygame.quit()