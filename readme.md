# Dev Log: Boids

## The Theory
Boids are an artificial life program which simulates the flocking behaviour of birds, and related group motion. They are an example of emergent behaviour: behaviour that arises from the interaction of individual agents adhering to a set of simple rules. The rules boids follow are:
- **Separation**: Steer to avoid crowing local flockmates
- **Alignment**: Steer towards the average heading of local flockmates
- **Cohesion**: Steer to move towards the average position of local flockmates

There are further rules which I may explore later, including:
- **Obstacle Detection**: Steer to avoid obstacles in the environment and the boundaries of the environment
- **Goal Seeking**: Steer towards a specified goal point

I will initially focus on the main 3 rules for boids and from there I can consider adding more complex rules.

## Log 1: Basic Boids
To start, I set up a pygame environment which the boids would end up flying around in. From there, I could begin to implement a class for boids.

### Boids Class
The most basic boids class requires x and y coordinates and velocity in x and y directions. All boids will have the same overall speed (i.e. scalar speed will be the same but can have any vector combination to make it).

All boids will also have the same size, shape and same general to keep everything uniform but I will add some randomness to the colour of each boid so there is some way of differentiating each.

```python
class Boid():
    def __init__(self, x, y, speed=(1, 1), colour=(255, 255, 255)):
        self.x, self.y = x, y

        # Lambda function to generate a random variance number
        variance = lambda: r.randint(-3, 3)
        self.colour = (colour[0] + variance(), colour[1] + variance(), colour[2] + variance())

        self.vx, self.vy = speed

    def UpdatePosition(self):
        """Update the position of the boid based on its velocity."""
        self.x += self.vx
        self.y += self.vy

    def Draw(self, screen):
        """Draw the boid on the given screen."""
        pygame.draw.circle(screen, self.colour, (int(self.x), int(self.y)), 5)
```

This gave us very basic boids which would simply move diagonally downwards without any behaviour.

From here I then created a temporary manager for these boids in the main script for the program which constructs a pre-determined number of boids and stores them in a list. They are also given random positions somewhere on the screen.

```python
boids = []
for i in range(NUM_BOIDS):
    # Create a boid with random position and default speed and color
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT)
    new_boid = Boid(x, y, colour=BOID_COLOUR)
    boids.append(new_boid)
```

Next thing to do was to make sure these boids didn't leave and never come back, which involved adding bounds detection. This isn't the same as the bounds detection rule they would have with more complex behaviours but it will do nicely for now.

```python
self.x = (self.x + self.vx) % self.bounds[0]
self.y = (self.y + self.vy) % self.bounds[1]
```

This instead allows the boid to move in any area within the bounds and the mod function keeps the coordinates in the range of the screen (e.g. if the bounds on the $x$-axis are 800 and a boid is at 801, $801 \; mod \; 800 = 1$ so the boid will teleport to the other side of the screen).

Now I wanted to add a way for boids to all have the same speed but start moving in random directions. For this, I looked back to my trigonometry knowledge, specifically the parametric equations of a circle:

$$
x = rcos(t) \\
y = rsin(t)
$$

Applying these to the boids you get:
```python
# Generate random angles for sin and cos
angle = r.randint(0, 360)

# Calculate sin and cos of the angle multiplied by speed (using parametric equations)
self.vx = speed * math.cos(angle)
self.vy = speed * math.sin(angle)
```

This left us with an environment where boids start moving in random directions and 