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

This left us with an environment where boids start moving in random directions.

## Log 2: Separation
After some research, I found out a good method of implementing the rules - starting with separation.

Before I can do that, though, it is best I work on the system which will allow boids to detect eachother's presence.

### Spacial Partitioning
To hopefully improve performance in the long run, I'm planning on implementing spatial partitioning for this system. This allows for each boid to only need to search a part of the world space (which I will call the universe) instead of the entire universe.

The universe will be split into a grid of squares and each boid will be assigned a code or hash based on what square they are in. From there, if a boid needs to check for other boids, it only needs to check the surrounding squares.

First, we start by creating a class for the universe which the boids will live in. This should be able to keep track of all currently existing boids, the partitions for the universe space as well as any information about the universe such as width and height.

```python
class Universe:
    def __init__(self, width, height, boid_number, boid_colour):
        self.width = width
        self.height = height
        self.boid_number = boid_number
        self.boid_colour = boid_colour
        self.boids = []

        self.partition_size = 100
        self.partitions = {}
```

From here we also need a setup function which will allow us to create all the boids at once.

```python
def setup(self):
    """Create all boids and add them to the list of boids"""
    for _ in range(self.boid_number):
        # Create a boid with random position and default speed and color
        x = random.randint(0, self.width)
        y = random.randint(0, self.height)

        new_boid = Boid(x, y, 
            speed=3, 
            colour=self.boid_colour, 
            bounds=(self.width, self.height)
        )
        
        self.boids.append(new_boid)
```

Now we can focus on creating the spacial partitioning system. First, we need to be able to update the partition values for every single boid.

```python
def update_partitions(self):
    """Update what partition each boid is in"""

    # Clear all previous positions
    self.partitions.clear()

    for b in self.boids:
        # Creating key for the boid
        cell_x = int(b.x // self.partition_size)
        cell_y = int(b.y // self.partition_size)
        key = (cell_x, cell_y)

        # Checking if we have that key in the section
        if key not in self.partitions:
            self.partitions[key] = []
        self.partitions[key].append(b)
```

Here, we simply take the x and y coordinates for each boid and divide them by the partition size to split the grid up into equal squares. We can use these new grid coordinates to make a key for that boid which we can use to add the boid to the partitioning dictionary.

We now also need a way to get the neighbours of a boid within a certain radius to calculate and evaluate our rules.

```python
def get_neighbours(self, boid, radius=10):
    neighbours = []

    # Getting grid coordinates for current boid
    cell_x = int(boid.x // self.partition_size)
    cell_y = int(boid.y // self.partition_size)

    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            key = (cell_x + dx, cell_y + dy)
            # Loop through all boids in that partition and check if they are within the radius
            for b in self.partitions[key]:
                dist = math.sqrt((boid.x - b.x)**2 + (boid.y - b.y)**2)
                if dist <= radius:
                    neighbours.append(b)

    return neighbours
```

With this created we now needed a function to update everything in the universe.

```python
def update_universe(self, screen):
    self.update_partitions()
    for b in self.boids:
        b: Boid
        neighbours = self.get_neighbours(b)
        b.UpdatePosition()
        b.Draw(screen)
```

With this we can now start working on the first rule: **separation**. This rule states that boids should steer to avoid contact with nearby boids. The best way to achieve this is for a boid **b**, to have all closely neighbouring boids to b apply a force to b which pushes it away from that boid.

To start, I decided to switch from using tuples for positions and velocities to `pygame.Vector2` objects as these would provide us with some useful functions. At the same time I added a separation parameter to the boids.

```python
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

...

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
```

From here we can work on our separation function.

```python
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
```

We can now add this to the update position function so it runs before updating the position of the boid.

```python
def update_universe(self, screen):
    self.update_partitions()
    for b in self.boids:
        b: Boid
        neighbours = self.get_neighbours(b)
        b.ApplySeparationForce(neighbours)
        b.UpdatePosition()
        b.Draw(screen)
```

From here I immediately realised it is probably best to make a dedicated update function in the boid so the universe update function isn't handling too much.

```python
# In Boid Class...
def Update(self, neighbours, screen):
    # Apply all forces from rules
    self.ApplySeparationForce(neighbours)

    # Update position using newly updated acceleration
    self.UpdatePosition()

    # Draw boid to the screen
    self.Draw(screen)

# In Universe Class...
def update_universe(self, screen):
    self.update_partitions()
    for b in self.boids:
        b: Boid
        neighbours = self.get_neighbours(b)
        b.Update(neighbours, screen)
```

Much cleaner now. We also now have a much cleaner main loop for the simulation:

```python
NUM_BOIDS = 10  # Number of boids to create
BOID_COLOUR = (176, 224, 230)

universe = Universe(SCREEN_WIDTH, SCREEN_HEIGHT, NUM_BOIDS, BOID_COLOUR)
universe.setup()

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
    universe.update_universe(SCREEN)

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    CLOCK.tick(60)

pygame.quit()
```

Thanks to the universe handling most of the updates in the `update_universe()` function. It was at this point that the variance in my naming convensions for functions bugged me so I changed them all.

And with that the separation rule was complete!