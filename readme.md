# Dev Log: Boids

<figure align="center">
    <img src="./assets//boids.gif" width="400" />
    <figcaption>Figure 1: Boids simulation in Python</figpython>
</figure>

## How to Run
To run the application, download the latest release and then:

1. Run `pip install -r requirements.txt` to get all modules used
2. Run `main.py`

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

## Log 3: Alignment
Now onto the second rule which is **alignment**. This states that boids should steer towards the average heading of local flockmates.

For this, for every boid, b, we can get the direction of nearby flockmates and apply a force which turns b in that direction.

As I was developing this, I realised that looping over the neighbours again for each rule is unnecessary when instead we can loop over all neighbours once and calculate all forces at once.

I also added a function to apply multiple forces in one function call.

```python
def _ApplyForces(self, *forces:list[pygame.Vector2]):
    for f in forces:
        self.acceleration = self.acceleration + f
```

New function for applying forces from rules looks like this:

```python
def _ApplyRuleForces(self, neighbours:list['Boid']):
    separation_force = pygame.Vector2()
    alignment_force = pygame.Vector2()
    
    num = len(neighbours)

    # Ignore function if there are no neighbours
    if num == 0: return

    for n in neighbours:
        n: Boid

        # Adding averaged velocity to the alignment force
        alignment_force += n.velocity / num

        displacement = self.position - n.position
        distance = self.position.distance_to(n.position)

        # We scale the separation force applied by the distance to the boid
        if distance != 0:
            displacement /= distance
        separation_force += displacement
    
    # Normalising the alignment force so that it doesn't exceed max speed
    alignment_force = alignment_force.normalize() * self.max_speed
    alignment_force -= self.velocity
    
    self._ApplyForces(separation_force, alignment_force)
```

You may also notice I've now made a bunch of functions in the boid private so I don't accidentally apply a force to the boid from an external class.

Once this alignment implementation was in it seemed like the boids were jolting around instead of smoothly changing direction and I realised this was because sometimes the force applied to the boid was so large that it caused an instantaneous switch in direction.

To resolve this, I gave the boids a maximum force that can be applied to them at any one time and clamped the force calculated in the `_ApplyRulesForce()` so it can never go over that value. I also gave them a larger radius so that they had more boids to average at one time.

```python
# Normalising the alignment force so that it doesn't exceed max speed
alignment_force = alignment_force.normalize() * self.max_speed
alignment_force -= self.velocity
if alignment_force.magnitude() > 0: alignment_force = alignment_force.clamp_magnitude(self.max_force)
```

To check the directions of boids more easily I also took this time to change the shape of boids from circles to triangles.

```python
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
```

(I'm doing as much of this by myself as I can but that was a ChatGPT special).

From here I was still having a lot of jolting and this is where I realised the separation force was largely overpowering the alignment force as I hadn't clamped or averaged it in the `_ApplyRuleForces()` function.

Another thing I noticed was that I would get errors in my `_ApplyRulesForces()` function due to trying to normalise a 0 vector. I had already added a check to skip the function if there were no neighbours so this meant there was somehow a case where there could be a neighbour and still 0 forces applied.

It took a little browse to realise that I wasn't checking to see if a neighbour found in the `GetNeighbours()` function was actually the boid itself. Once I had done this the boids were moving smoothly round the place without needs to check for 0 vectors.

```python
def GetNeighbours(self, boid:Boid, radius=30):
    ...

    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            key = (cell_x + dx, cell_y + dy)
            for b in self.partitions[key]:
                if b == boid: continue

                ...
```

I also added another check in the `_ApplyRulesForces()` so that no zero vectors could get through.

```python
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
```

Ugly but it works

At this point I also wanted to do a quick check of performance and see if my spacial partitioning gave me the speed I was hoping for. For this, I increased the number of boids to 300 and checked the fps. I also quickly programmed a function to calculate the average fps while running the simulation and a timer which sets total simulation time to 0

```python
elapsed = (pygame.time.get_ticks() - start_time) / 1000
if elapsed >= total_time:
    PrintResults(avg)
    running = False
```

These were the results:

| Boid Num | Screen Size | Average FPS |
| -------- | ----------- | ----------- |
| 200      | 1000×800    | 105.3       |
| 200      | 1920×1080   | 144.9       |
| 300      | 1000×800    | 48.5        |
| 300      | 1920×1080   | 75.8        |

It was interesting to see that increasing screen size increased the framerate no matter the boid number however after some critical thinking it made a lot of sense. With a larger screen size, boids have more space and therefore are less likely to encounter neighbours so less neighbours will need to be iterated through in the force calculations.

With this 2 of the 3 rules had been implemented!

## Log 3: Cohesion
And then there was one. The final rule to implement was **cohesion**. This rule states that boids should steer to move towards the average position of local flockmates.

To do this my first thought was to get all neighbours of a boid b, average out their position (avg_pos) add a force along the vector from b to avg_pos.

```python
if cohesion_force.length() != 0:
    cohesion_force -= self.position
    cohesion_force.normalize() * self.max_speed
    cohesion_force -= self.velocity
    if cohesion_force.length() != 0:
        cohesion_force = cohesion_force.clamp_magnitude(self.max_force)
```

Once this was implmeneted I realised that the alignment and cohesion forces were overpowering the separation forces. For this I added a slight multiplier to the separation force clamp so It could reach a higher max force.

And with that the main simulation was done!

From here it is just fun additions to the system if I can be asked.